import exprs
import stypes

# maps symbols to functions which compile lists which have as first
# element that same symbol
handlers = {}

def handler(symname):
    symbol = stypes.Symbol.from_str(symname)
    
    def decorator(func):
        handlers[symbol] = func
        return func
    
    return decorator


@handler('set!')
def assignments(slist):
    def validate():
        # Returns the variable and sub-expression if @slist is
        # valid. ValueError is raised otherwise.
        
        def raiseit():
            raise ValueError(f'{slist} is not a valid assignment expression')
        
        cdr = slist.cdr
        if type cdr is not stypes.Cons:
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
            raise ValueError(f'{slist} is not a valid assignment expression')
        
        cdr = slist.cdr
        if type cdr is not stypes.Cons:
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
    subexpr = exprs.DefinitionExpr(var, subexpr)
    return subexpr


@handler('if')
def ifexpr(slist):
    predicate = compile(slist.car)
    consequent = compile(slist.cdr.car)
    cddr = slist.cdr.cdr
    alternative = None if cddr is stypes.nil else compile(cddr.car)
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
    if type(body) is not Cons:
        raiseit()

    body = [compile(subexpr) for subexpr in body]
    return exprs.LambdaExpr(params, body)


@handler('begin')
def beginexpr(slist):
    return BeginExpr([compile(subexpr) for subexpr in slist.cdr])


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
        handler = handlers[first]
        return handler(sds)
    else:
        # @sds encodes an application expression.
        subexprs = [compile(element) for element in sds.pylist]
        return exprs.ApplicationExpr(subexprs)
