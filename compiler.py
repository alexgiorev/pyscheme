"""
The most important function in this module is compile. It's purpose is to
transform a scheme data structure (most commonly a list) to an expression
(i.e. an instance of Expr). Most of the functions in this module specialize in
compiling lists with predetermined Symbol heads and compile just dispatches to
these functions based on the first element of the list to compile.
"""

import exprs
import stypes

from stypes import *

# maps symbols to functions which compile lists which have as first
# element that same symbol
handlers = {}

def handler(symname):
    symbol = Symbol(symname)
    
    def decorator(func):
        handlers[symbol] = func
        return func
    
    return decorator


@handler('quote')
def compile_quote(slist):
    if type(slist.cdr) is not Cons:
        raise ValueError(f'Ill formed quote: {slist}')
    
    return exprs.QuoteExpr(slist.cadr)


@handler('set!')
def compile_assignment(slist):
    def validate():
        # Returns the variable and sub-expression if @slist is
        # valid. ValueError is raised otherwise.
        
        def raiseit(msg):
            raise ValueError(f'Ill formed assignment expression: {slist}')
        
        cdr = slist.cdr
        if type(cdr) is not Cons:
            raiseit()

        var = cdr.car
        if type(var) is not Symbol:
            raiseit()

        cddr = cdr.cdr
        if type(cddr) is not Cons:
            raiseit()

        subexpr = cddr.car
        return var, subexpr

    var, subexpr = validate()
    subexpr = compile(subexpr)
    return exprs.AssignmentExpr(var, subexpr)


@handler('define')
def compile_definition(slist):
    def validate():
        """Returns a pair (variable, sub-expression data structure) if (slist)
        is valid. Otherwise a ValueError is raised."""
        
        def raiseit():
            raise ValueError(f'Ill formed definition expression: {slist}')
        
        if type(slist.cdr) is not Cons:
            raiseit()
            
        if type(slist.cadr) is Symbol:
            # a variable definition
            var = slist.cadr
            
            if type(slist.cddr) is not Cons:
                raiseit()
                
            subexpr = slist.caddr
            return var, subexpr
        elif type(slist.cadr) is Cons: # a function definition
            if not slist.cadr.is_list:
                raiseit()
                
            for x in slist.cadr:
                if type(x) is not Symbol:
                    raiseit()
                    
            var = slist.cadr.car
            params = slist.cadr.cdr
            body = slist.cddr
            lambda_slist = Cons(Symbol('lambda'), Cons(params, body))
            return var, lambda_slist
        else:
            raiseit()
            
    var, subexpr = validate()
    # check for 'lambda' explicitly so that you can pass the variable
    # needed in order for the function to have name metadata
    if type(subexpr) is Cons and subexpr.car == Symbol('lambda'):
        subexpr = compile_lambda(subexpr, var)
    else:
        subexpr = compile(subexpr)
        
    return exprs.DefinitionExpr(var, subexpr)


@handler('if')
def compile_if(slist):
    try:
        l = slist.cdr
        predicate = l.car; l = l.cdr
        consequent = l.car; l = l.cdr
        alternative = None if l is stypes.nil else l.car
    except AttributeError: # caused by one of the l.cdr
        raise ValueError(f'Ill formed if expression: {slist}')
    
    predicate = compile(predicate)
    consequent = compile(consequent)
    alternative = None if alternative is None else compile(alternative)
    
    return exprs.IfExpr(predicate, consequent, alternative)


@handler('lambda')
def compile_lambda(slist, var=None):
    """(var) must be a Symbol or None."""
    
    def raiseit(msg):
        raise ValueError(f'{slist} is not a valid lambda expression: {msg}')

    if type(slist.cdr) is not Cons:
        raiseit('expected a list after the lambda')
    
    params = slist.cdr.car
    
    if type(params) is not Cons and params is not stypes.nil:
        raiseit('the parameters must be a list')
        
    try:
        params = params.pylist
    except ValueError: # params is a pair, but it may not be a list
        raiseit('the parameters must be a list')

    for param in params:
        if type(param) is not Symbol:
            raiseit('the elements of the parameter list must be symbols, '
                    f'but found {param}')

    body = slist.cdr.cdr
    if not (type(body) is Cons and body.is_list):
        raiseit(f'the body must be a list')

    body = [compile(subexpr) for subexpr in body]
    return exprs.LambdaExpr(params, body, var)


@handler('let')
def compile_let(slist):
    # transforms the let to a lambda application and compiles that
    
    def validate():
        """Makes sure slist is well formed. If not, a ValueError is raised.
        Returns a triple of scheme lists (params, body, arguments)."""
        
        def raiseit(msg):
            raise ValueError(f'invalid let expression: {slist}. {msg}')
    
        if type(slist.cdr) is not Cons:
            raiseit(f"Unexpected cdr after 'let: {slist.cdr}")
    
        bindings = slist.cadr

        if type(bindings) is not Cons:
            raiseit(f'bindings must be a list: {bindings}')

        try:
            bindings = list(bindings)
        except ValueError: # when bindings is not a list
            raiseit(f'bindings must be a list: {bindings}')
        
        body = slist.cddr
    
        if type(body) is not Cons or not body.is_list:
            raiseit(f'the body must be a list: {body}')
        
        params = []
        arguments = []

        for i, binding in enumerate(bindings):
            if type(binding) is not Cons:
                raiseit(f'The binding at position {i} is not a list pair.')

            params.append(binding.car)

            if type(binding.cdr) is not Cons:
                raiseit(f'The binding at position {i} is not a list pair.')

            arguments.append(binding.cadr)

        return Cons.iterable2list(params), body, Cons.iterable2list(arguments)

    params, body, arguments = validate()
    lambda_expr = Cons(Symbol('lambda'), Cons(params, body))
    app = Cons(lambda_expr, arguments)
    return compile_application(app)


@handler('begin')
def compile_begin(slist):
    if not (type(slist.cdr) is Cons and slist.cdr.is_list):
        raise ValueError(f'Ill formed begin expression: {slist}')
    
    return exprs.BeginExpr([compile(subexpr) for subexpr in slist.cdr])


@handler('cond')
def compile_cond(slist):    
    def raiseit():
        raise ValueError(f'Ill formed cond expression: {slist}')
    
    def validate_slist():
        """Returns a list of the cond's clauses if (slist) has a valid
        format. Otherwise, a ValueError is raised."""            
        cdr = slist.cdr
        if type(cdr) is not Cons:
            raiseit()

        if not cdr.is_list:
            raiseit()
            
        return list(cdr)

    def validate_clause(clause):
        """Returns a pair (<predicate>, <body>) if (clause) is valid. Otherwise
        calls (raiseit)."""
        
        if type(clause) is not Cons:
            raiseit()

        if not clause.is_list:
            raiseit()

        predicate, body = clause.car, clause.cdr
        body = Cons(Symbol('begin'), body)
        return predicate, body
    
    clauses = list(reversed(validate_slist()))

    predicate, body = validate_clause(clauses[0])
    if_accum = (compile_begin(body)
                if predicate is Symbol('else')
                else exprs.IfExpr(compile(predicate), compile_begin(body)))
    
    for clause in clauses[1:]:
        predicate, body = validate_clause(clause)
        
        if predicate is Symbol('else'):
            raiseit()
            
        if_accum = exprs.IfExpr(compile(predicate), compile_begin(body), if_accum)
        
    return if_accum


@handler('and')
def compile_and(slist):
    def raiseit():
        raise ValueError(f'Ill formed and expression: {slist}')
    
    cdr = slist.cdr
    
    if cdr is stypes.nil:
        return exprs.AndExpr([])
    
    if type(cdr) is not Cons:
        raiseit()

    if not cdr.is_list:
        raiseit()

    return exprs.AndExpr([compile(sublist) for sublist in cdr])


@handler('or')
def compile_or(slist):
    def raiseit():
        raise ValueError(f'Ill formed and expression: {slist}')
    
    cdr = slist.cdr
    
    if cdr is stypes.nil:
        return exprs.OrExpr([])
    
    if type(cdr) is not Cons:
        raiseit()

    if not cdr.is_list:
        raiseit()

    return exprs.OrExpr([compile(sublist) for sublist in cdr])
    

def compile_application(app):
    subexprs = [compile(element) for element in app.pylist]
    return exprs.ApplicationExpr(subexprs)


def compile(sds):
    """Transforms the scheme data structure @sds to an Expr object. If
    not possible, a ValueError is raised"""
    
    if type(sds) in (Number, String, Boolean):
        return exprs.SelfEvaluatingExpr(sds)
    elif type(sds) is Symbol:
        return exprs.VariableExpr(sds)

    # At this point @sds is a scheme list. Compile based on the first element.

    first = sds.car
    if type(first) is Symbol:
        handler = handlers.get(first)
        if handler is None:
            return compile_application(sds)
        else:
            return handler(sds)

    return compile_application(sds)

