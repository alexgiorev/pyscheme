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
def definition(slist):
    def validate():
        # Returns the variable and sub-expression if @slist is
        # valid. ValueError is raised otherwise.
        
        def raiseit():
            raise ValueError(f'"{slist}" is not a valid definition expression')
        
        cdr = slist.cdr
        
        if type(cdr) is not Cons:
            raiseit()
            
        cadr = cdr.car
        
        if type(cadr) is Symbol:
            # a variable definition
            var = cadr
            subexpr = cdr.cdr.car
            return var, subexpr
        elif type(cadr) is Cons:
            # a function definition
            
            for x in cadr:
                if type(x) is not Symbol:
                    raiseit()
                    
            var = cadr.car
            params = cadr.cdr
            body = cdr.cdr
            lambda_sym = Symbol('lambda')
            lambda_slist = Cons(lambda_sym, Cons(params, body))
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
    if type(params) is not Cons and params is not stypes.nil:
        raiseit()

    params = params.pylist

    for param in params:
        if type(param) is not Symbol:
            raiseit()

    body = slist.cdr.cdr
    if type(body) is not Cons:
        raiseit()

    body = [compile(subexpr) for subexpr in body]
    return exprs.LambdaExpr(params, body)


@handler('let')
def letexpr(slist):
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
def beginexpr(slist):
    return exprs.BeginExpr([compile(subexpr) for subexpr in slist.cdr])


def compile_application(app):
    subexprs = [compile(element) for element in app.pylist]
    return exprs.ApplicationExpr(subexprs)


def compile(sds):
    '''Transforms the scheme data structure @sds to an Expr object. If
    not possible, a ValueError is raised'''
    
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

