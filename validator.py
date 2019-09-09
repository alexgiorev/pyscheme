from stypes import *
from utils import iter_is_empty, is_list

# separate validators for each type of schema
validators = {}

def validator(stype):
    def decorator(func):
        validators[stype] = func
        return func
    return decorator

def isvalid(scm, obj):
    stype = scmtype(scm)
    return validators[stype](scm, obj)

def scmtype(schema):
    if type(schema) is tuple:
        return schema[0]
    elif type(schema) is list:
        return 'list'
    elif type(schema) is str:
        return schema
    else:
        raise ValueError(f'Invalid schema: {schema}')

@validator('symbol')
def sym_vldtr(ss, obj):
    if type(obj) is not Symbol:
        return False
    sn = name(ss)
    return sn is None or sn == obj.name

def name(schema):
    if type(schema) is str:
        return None
    else:
        return schema[1]

@validator('list')
def list_vldtr(ls, obj):
    if not is_list(obj):
        return False

    def rest(atleast_one):
        isempty, objs = iter_is_empty(objects)
        if isempty:
            return not atleast_one
        for obj in objs:
            if not isvalid(restscm, obj):
                return False
        return True            
    
    objects, schemas = iter(obj), children(ls)
    for child in schemas:
        if child in ('rest', 'rest+'):
            try: restscm = next(schemas)
            except StopIteration:
                raise ValueError(f'Expected a schema after "rest"')            
            return rest(child == 'rest+')
        elif child == 'rest+':
            restplus(); break
        else:
            nxt = next(objects, None)
            if nxt is None or not isvalid(child, nxt):
                return False
    return next(objects, None) is None
                
def children(ls):
    if type(ls) is tuple:
        return iter(ls[1])
    elif type(ls) is list:
        return iter(ls)
    else:
        raise ValueError(f'Invalid list schema: {ls}')

@validator('any')
def any_vldtr(scm, obj):
    return True

if __name__ == '__main__':
    import parser

    def parse(astr):
        return parser.parse(astr).car
    
    quote = [('symbol', 'quote'), 'any']
    assignment = [('symbol', 'set!'), 'symbol', 'any']
    ifexpr =  [('symbol', 'if'), 'any', 'optional', 'any']
    lambdaexpr = [('symbol', 'lambda'), ['rest', 'symbol'], 'rest+', 'any']
    letexpr = [('symbol', 'let'), ['rest', ['symbol', 'any']], 'rest+', 'any']
    begin = [('symbol', 'begin'), 'rest+', 'any']
    cond = [('symbol', 'cond'), 'rest+', ['any', 'rest+', 'any']]

    assert isvalid(quote, parse('(quote me)'))
    assert not isvalid(quote, parse('(quote)'))
    assert not isvalid(quote, parse('(quote me and you)'))
    assert isvalid(assignment, parse('(set! a (+ b 10))'))
    assert not isvalid(assignment, parse('(set! 10 15)'))
    assert not isvalid(assignment, parse('(set a 5)'))
    assert not isvalid(assignment, parse('(set! a)'))
    assert isvalid(lambdaexpr, parse('(lambda (a b) (define c (+ a b)) (+ a b c))'))
    assert isvalid(lambdaexpr, parse('(lambda () do-something)'))
    assert not isvalid(lambdaexpr, parse('(lambda (a b c))'))
    assert isvalid(letexpr, parse('(let ((a 1) (b 2) (c 3)) (+ a b c 1))'))
    assert isvalid(letexpr, parse('(let () (+ 3 4))'))
    assert isvalid(letexpr, parse('(let ((a 1)) (+ a b))'))
    assert not isvalid(letexpr, parse('(let ((3 4) (5 6)) (+ 3 5))'))
    assert not isvalid(letexpr, parse('(let ((a 1) (b 2)))'))
    assert isvalid(begin, parse('(begin (define a 1) (define b 2) (+ a b))'))
    assert not isvalid(begin, parse('begin'))
    assert not isvalid(begin, parse('(begin)'))
    assert isvalid(cond, parse('(cond ((even? a) expr1 expr2) (else else-expr))'))
