import stypes
import steptools

from frame import Frame
from exceptions import *
from stypes import *
from environment import Environment

class Expr:
    """Base class for all expressions.
    * attributes for instances of subclasses
    - self.main_step: a callable which accepts a single interpreter argument. It
      should be evaluatable an arbitrary number of times."""
    pass


class SelfEvaluatingExpr(Expr):
    def __init__(self, value):
        self.value = value
        self.main_step = steptools.Identity(value)

    def __str__(self):
        return str(self.value)

    
class QuoteExpr(Expr):
    def __init__(self, slist):
        self.slist = slist
        self.main_step = steptools.Identity(slist)

    def __str__(self):
        return f'(quote {self.slist})'

    
class VariableExpr(Expr):
    def __init__(self, var):
        self.var = var
        self.main_step = lambda inter: inter.env.lookup(self.var)

    def __str__(self):
        return str(self.var)

        
class AssignmentExpr(Expr):
    def __init__(self, var, subexpr):
        self.var = var
        self.subexpr = subexpr
        self.main_step = self._create_main_step(var, subexpr)

    @staticmethod
    def _create_main_step(var, subexpr):
        subexpr_main_step = subexpr.main_step
        
        def value_handler(inter):
            inter.env.set_variable_value(var, inter.last_value)
            
        def main_step(inter):
            inter.step_stack.append(value_handler)
            inter.step_stack.append(subexpr_main_step)
            
        return main_step

    def __str__(self):
        return f'(set! {self.var} {self.subexpr})'

    
class DefinitionExpr(Expr):
    def __init__(self, var, subexpr):
        self.var = var
        self.subexpr = subexpr
        self.main_step = self._create_main_step(var, subexpr)

    @staticmethod
    def _create_main_step(var, subexpr):
        subexpr_main_step = subexpr.main_step
        
        def value_handler(inter):
            inter.env.define_variable(var, inter.last_value)
            
        def main_step(inter):
            inter.step_stack.append(value_handler)
            inter.step_stack.append(subexpr_main_step)
            
        return main_step

    def __str__(self):
        return f'(define {self.var} {self.subexpr})'

    
class IfExpr(Expr):
    def __init__(self, predicate, consequent, alternative=None):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative
        self.main_step = self._create_main_step(predicate, consequent, alternative)

    @staticmethod
    def _create_main_step(predicate, consequent, alternative):
        predicate_step = predicate.main_step
        consequent_step = consequent.main_step
        alternative_step = None if alternative is None else alternative.main_step
        
        def pred_value_handler(inter):
            if inter.last_value is stypes.false:
                if alternative is None:
                    return stypes.unspecified
                inter.step_stack.append(alternative_step)
            else:
                inter.step_stack.append(consequent_step)

        def main_step(inter):
            inter.step_stack.append(pred_value_handler)
            inter.step_stack.append(predicate_step)

        return main_step

    def __str__(self):
        return (f'(if {self.predicate} {self.consequent})'
                if self.alternative is None
                else f'(if {self.predicate} {self.consequent} {self.alternative})')

    
class LambdaExpr(Expr):
    def __init__(self, params, body, var=None):
        """(params) must be a sequence of variables. (body) must be a sequence
        of expressions. (var) must be either None or a Symbol."""
        self.params = params
        self.body = body
        self.funcname = None if var is None else String(var.name)
        self.main_step = self._create_main_step(params, body, self.funcname)

    @staticmethod
    def _create_main_step(params, body, funcname):
        compiled_body = BeginExpr(body).main_step
        return (lambda inter:
                CompoundProcedure(params, compiled_body, inter.env, funcname))

    def __str__(self):
        params_str = f"({' '.join(str(param) for param in self.params)})"
        body_str = ' '.join(str(expr) for expr in self.body)
        return f'(lambda {params_str} {body_str})'

    
class BeginExpr(Expr):
    def __init__(self, exprs):
        # @exprs must be a non-empty sequence of expressions
        self.exprs = exprs
        self.main_step = self._create_main_step(self.exprs)

    @staticmethod
    def _create_main_step(exprs):
        steps_reversed = [expr.main_step for expr in reversed(exprs)]
        return (lambda inter:
                inter.step_stack.extend(steps_reversed))

    def __str__(self):
        exprs_str = ' '.join(str(expr) for expr in self.exprs)
        return f'(begin {exprs_str})'

    
class ApplicationExpr(Expr):
    def __init__(self, exprs):
        """(exprs) must be a non-empty iterable of Exprs."""
        self.exprs = list(exprs)
        self.main_step = self._create_main_step(exprs)

        
    @staticmethod
    def _create_main_step(exprs):        
        def values_handler(inter):
            values = inter.last_value # the list of sub-expressions' values
            operator = values[0]
            operands = values[1:]
            inter.step_stack.append(steptools.Caller(operator, operands))
        
        steps = [expr.main_step for expr in exprs]
        def main_step(inter):
            inter.step_stack.append(values_handler)
            inter.step_stack.append(steptools.Sequencer(iter(steps)))

        return main_step

    
    def __str__(self):
        return f"({' '.join(str(expr) for expr in self.exprs)})"


class AndExpr(Expr):
    def __init__(self, exprs):
        """(exprs) must be an iterable of Expr instances."""
        self.exprs = list(exprs)        
        self.main_step = self._create_main_step(self.exprs)

        
    @staticmethod
    def _create_main_step(exprs):
        if not exprs:
            return steptools.Identity(stypes.true)

        def main_step(inter):
            steps = (expr.main_step for expr in exprs)
            first_step = next(steps)
            looper = AndExpr._looper(steps)
            inter.step_stack.append(looper)
            inter.step_stack.append(first_step)
            
        return main_step


    @staticmethod
    def _looper(steps):
        """(steps) must be an iterator of steps."""
        def looper(inter):
            last_value = inter.last_value
            
            if last_value is stypes.false:
                return stypes.false
            
            try:
                next_step = next(steps)
            except StopIteration:
                return last_value

            step_stack = inter.step_stack
            step_stack.append(looper)
            step_stack.append(next_step)

        return looper

    
    def __str__(self):
        return f"(and {' '.join(str(expr) for expr in self.exprs)})"


class OrExpr(Expr):
    def __init__(self, exprs):
        """(exprs) must be an iterable of Expr instances."""
        self.exprs = list(exprs)
        self.main_step = self._create_main_step(self.exprs)

        
    @staticmethod
    def _create_main_step(exprs):
        if not exprs:
            return steptools.Identity(stypes.false)

        def main_step(inter):
            steps = (expr.main_step for expr in exprs)
            first_step = next(steps)
            looper = OrExpr._looper(steps)
            inter.step_stack.append(looper)
            inter.step_stack.append(first_step)
            
        return main_step


    @staticmethod
    def _looper(steps):
        """(steps) must be an iterator of steps."""
        def looper(inter):
            last_value = inter.last_value
            
            if last_value is not stypes.false:
                return last_value
            
            try:
                next_step = next(steps)
            except StopIteration:
                return last_value

            step_stack = inter.step_stack
            step_stack.append(looper)
            step_stack.append(next_step)

        return looper

    
    def __str__(self):
        return f"(or {' '.join(str(expr) for expr in self.exprs)})"
