import stypes

from frame import Frame
from exceptions import *
from environment import Environment

class Expr:
    """Base class for all expressions.
    * attributes for instances of subclasses
    - self.main_step: a callable which accepts a single inter argument. It should be
      evaluatable an arbitrary number of times."""
    pass


class SelfEvaluatingExpr(Expr):
    def __init__(self, value):
        self.value = value
        self.main_step = lambda inter: value

    def __str__(self):
        return str(self.value)

class QuoteExpr(Expr):
    def __init__(self, slist):
        self.slist = slist
        self.main_step = lambda inter: slist

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
    def __init__(self, predicate, consequent, alternative):
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
    def __init__(self, params, body):
        # params must be a sequence of variables
        # body must be a non-empty sequence of expressions
        self.params = params
        self.body = body
        self.main_step = self._create_main_step(params, body)

    @staticmethod
    def _create_main_step(params, body):
        compiled_body = BeginExpr(body).main_step
        return (lambda inter:
                stypes.CompoundProcedure(params, compiled_body, inter.env))

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
        # @exprs must be a non-empty sequence of expressions
        self.exprs = exprs
        self.main_step = self._create_main_step(exprs)

    @staticmethod
    def _create_main_step(exprs):        
        def values_handler(inter):
            values = inter.last_value # the list of sub-expressions' values
            operator = values[0]
            operands = values[1:]
            
            if type(operator) is stypes.PrimitiveProcedure:
                return operator(inter, *operands)
            elif type(operator) is stypes.CompoundProcedure:
                params, step, env = operator.parts
                
                if len(params) != len(operands):
                    raise SchemeArityError(f'Expected {len(params)} arguments, '
                                           f'but got {len(operands)}.')
                
                new_env = Environment(params, operands, env)
                
                if not inter.step_stack: # tail call optimization
                    inter.frame_stack.pop()
                    
                inter.frame_stack.append(Frame(step, new_env))
            else:
                raise SchemeTypeError(f'{operator} is not applicable')
        
        steps = [expr.main_step for expr in exprs]
        def main_step(inter):
            inter.step_stack.append(values_handler)
            inter.step_stack.append(Sequencer(iter(steps)))

        return main_step

    def __str__(self):
        return f"({' '.join(str(expr) for expr in self.exprs)})"


class Sequencer:
    """The result of a Sequencer is a list of the values of it's expressions in the same
    order."""
    
    def __init__(self, steps):
        """@steps must be a non-empty iterator of steps."""
        self.steps = steps
        self.result = []

        
    def value_handler(self, inter):
        self.result.append(inter.last_value)
        next_step = next(self.steps, None)
        
        if next_step is None:
            return self.result

        inter.step_stack.append(self.value_handler)
        inter.step_stack.append(next_step)
        
        
    def __call__(self, inter):
        first_step = next(self.steps)
        inter.step_stack.append(self.value_handler)
        inter.step_stack.append(first_step)
        
