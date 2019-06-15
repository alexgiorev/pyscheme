import exprs
import stypes

from stypes import *

# maps symbols to functions which compile lists which have as first
# element that same symbol
handlers = {}

def handler(symname):
    symbol = stypes.Symbol(symname)
    
    def decorator(func):
        handlers[symbol] = func
        return func
    
    return decorator


@handler('quote')
def quoteexpr(slist):
    cadr = slist.cdr.car
    return exprs.QuoteExpr(cadr)


@handler('set!')
def assignments(slist):
    def validate():
        # Returns the variable and sub-expression if @slist is
        # valid. ValueError is raised otherwise.
        
        def raiseit():
            raise ValueError(f'{slist} is not a valid assignment expression')
        
        cdr = slist.cdr
        if type(cdr) is not stypes.Cons:
            raiseit()

        var = cdr.car
        if type(var) is not stypes.Symbol:
            raiseit()

        cddr = cdr.cdr
        if type(cddr) is not stypes.Cons:
            raiseit()

        subexpr = cddr.car
        return var, subexpr

    var, subexpr = validate()
    subexpr = compile(subexpr)
    return exprs.AssignmentExpr(var, subexpr)


@handler('define')
def definition(slist):
    def validate():
        # Returns the variable and sub-expression if @slist is
        # valid. ValueError is raised otherwise.
        
        def raiseit():
            raise ValueError(f'"{slist}" is not a valid definition expression')
        
        cdr = slist.cdr
        
        if type(cdr) is not stypes.Cons:
            raiseit()
            
        cadr = cdr.car
        
        if type(cadr) is stypes.Symbol:
            # a variable definition
            var = cadr
            subexpr = cdr.cdr.car
            return var, subexpr
        elif type(cadr) is stypes.Cons:
            # a function definition
            
            for x in cadr:
                if type(x) is not stypes.Symbol:
                    raiseit()
                    
            var = cadr.car
            params = cadr.cdr
            body = cdr.cdr
            lambda_sym = stypes.Symbol('lambda')
            lambda_slist = stypes.Cons(lambda_sym, stypes.Cons(params, body))
            return var, lambda_slist
        else:
            raiseit()
            
    var, subexpr = validate()
    subexpr = compile(subexpr)
    return exprs.DefinitionExpr(var, subexpr)


@handler('if')
def ifexpr(slist):
    predicate = compile(slist.cdr.car)
    consequent = compile(slist.cdr.cdr.car)
    cdddr = slist.cdr.cdr.cdr
    alternative = None if cdddr is stypes.nil else compile(cdddr.car)
    return exprs.IfExpr(predicate, consequent, alternative)


@handler('lambda')
def lambdaexpr(slist):
    def raiseit():
        raise ValueError(f'{slist} is not a valid lambda expression')
        
    params = slist.cdr.car
    if type(params) is not stypes.Cons:
        raiseit()

    params = params.pylist

    for param in params:
        if type(param) is not stypes.Symbol:
            raiseit()

    body = slist.cdr.cdr
    if type(body) is not stypes.Cons:
        raiseit()

    body = [compile(subexpr) for subexpr in body]
    return exprs.LambdaExpr(params, body)


@handler('let')
def letexpr(slist):
    def tolambda(slist):
        bindings = slist[1]
        body = slist.cddr        
        params = [binding.car for binding in bindings]
        arguments = [binding.cadr for binding in bindings]
        lambda_expr = [Symbol('lambda'), 

@handler('begin')
def beginexpr(slist):
    return exprs.BeginExpr([compile(subexpr) for subexpr in slist.cdr])


def compile(sds):
    '''Transforms the scheme data structure @sds to an Expr object. If
    not possible, a ValueError is raised'''
    
    if type(sds) in (stypes.Number, stypes.String, stypes.Boolean):
        return exprs.SelfEvaluatingExpr(sds)
    elif type(sds) is stypes.Symbol:
        return exprs.VariableExpr(sds)

    # At this point @sds is a scheme list. Compile based on the first element.

    first = sds.car
    if type(first) is stypes.Symbol:
        handler = handlers.get(first)
        if handler is not None:
            return handler(sds)

    # @sds encodes an application expression.
    subexprs = [compile(element) for element in sds.pylist]
    return exprs.ApplicationExpr(subexprs)

