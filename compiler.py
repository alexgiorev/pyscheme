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
from validator import isvalid

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
    scm = [('symbol', 'quote'), 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid quote expression: {slist}')    
    return exprs.QuoteExpr(slist.cadr)


@handler('set!')
def compile_assignment(slist):
    scm = [('symbol', 'set!'), 'symbol', 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid set! expression: {slist}')    
    var, subexpr = slist.extract(1, 2)
    return exprs.AssignmentExpr(var, compile(subexpr))


@handler('define')
def compile_definition(slist):
    varscm = [('symbol', 'define'), 'symbol', 'any']
    funcscm = [('symbol', 'define'), ['rest+', 'symbol'], 'rest+', 'any']
    if isvalid(varscm, slist):
        var, subexpr = slist.extract(1, 2)
        compiled = (compile_lambda(subexpr, var)
                    if type(subexpr) is Cons and subexpr.car == Symbol('lambda')
                    else compile(subexpr))        
    elif isvalid(funcscm, slist):
        var, params, body = slist[1][0], slist[1].cdr, slist.nthcdr(2)
        lexpr = Cons(Symbol('lambda'), Cons(params, body))
        compiled = compile_lambda(lexpr, var)
    else:
        raise ValueError(f'Invalid definition: {slist}')                
    return exprs.DefinitionExpr(var, compiled)


@handler('if')
def compile_if(slist):
    if isvalid([('symbol', 'if'), 'any', 'any', 'any'], slist):
        pred, cons, alt = map(compile, slist.extract(1, 2, 3))
    elif isvalid([('symbol', 'if'), 'any', 'any']):
        pred, cons, alt = map(compile, slist.extract(1, 2)), None        
    return exprs.IfExpr(pred, cons, alt)


@handler('lambda')
def compile_lambda(slist, var=None):
    """(var) must be a Symbol or None. It is used as the name of the function
    being created."""
    scm = [('symbol', 'lambda'), ['rest', 'symbol'], 'rest+', 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid lambda expression: {slist}')
    params, body = slist[1], slist.nthcdr(2)
    compiled = [compile(sub) for sub in body]
    return exprs.LambdaExpr(params, compiled, var)


@handler('let')
def compile_let(slist):
    """Transforms the let to a lambda application and compiles that."""    
    scm = [('symbol', 'let'), ['rest', ['symbol', 'any']], 'rest+', 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid let expression: {slist}')
    bindings, body = slist[1], slist.nthcdr(2)
    params = Cons.from_iter(b[0] for b in bindings)
    args = Cons.from_iter(b[1] for b in bindings)    
    lambda_expr = Cons(Symbol('lambda'), Cons(params, body))
    app = Cons(lambda_expr, args)
    return compile_application(app)


@handler('begin')
def compile_begin(slist):
    scm = [('symbol', 'begin'), 'rest+', 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid begin expression: {slist}')
    return exprs.BeginExpr([compile(subexpr) for subexpr in slist.cdr])


@handler('cond')
def compile_cond(slist):    
    scm = [('symbol', 'cond'), 'rest+', ['any', 'rest+', 'any']]
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid cond expression: {slist}')    
    clauses = iter(slist.cdr)
    def makeif():
        clause = next(clauses, None)
        if clause is None:
            return None
        pred, conseq = clause.car, Cons(Symbol('begin'), clause.cdr)
        if pred == Symbol('else'):
            return compile(conseq)
        return exprs.IfExpr(compile(pred), compile(conseq), makeif())
    return makeif()


@handler('and')
def compile_and(slist):
    scm = [('symbol', 'and'), 'rest', 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid and expression: {slist}')
    return exprs.AndExpr(map(compile, slist.cdr))


@handler('or')
def compile_or(slist):
    scm = [('symbol', 'or'), 'rest', 'any']
    if not isvalid(scm, slist):
        raise ValueError(f'Invalid "or" expression: {slist}')
    return exprs.OrExpr(map(compile, slist.cdr))


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

