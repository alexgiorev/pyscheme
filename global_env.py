"""All of the functions in the global environment are defined here"""

import functools
import operator

import stypes
from environment import Environment
from exceptions import *

def make():
    return Environment.from_dict(namespace, None)

namespace = {} # maps symbols to functions

def globalfunc(varstr):
    symbol = stypes.Symbol.from_str(varstr)
    def decorator(func):        
        namespace[symbol] = stypes.PrimitiveProcedure(func)
    return decorator

################################################################################
# numeric

@globalfunc('+')
def _(*args):
    return sum(args, stypes.Number(0))

@globalfunc('-')
def _(*args):
    return sum((-num for num in args), stypes.Number(0))

@globalfunc('*')
def _(*args):
    return functools.reduce(operators.mul, args, stypes.Number(1))

@globalfunc('/')
def _(a, b):
    return a / b

@globalfunc('sub1')
def _(x):
    return x - stypes.Number(1)

@globalfunc('add1')
def _(x):
    return x + stypes.Number(1)

################################################################################
# pairs. TODO: map, fold, reduce...

@globalfunc('cons')
def _(a, b):
    return stypes.Cons(a, b)

@globalfunc('car')
def _(pair):
    if type(pair) is not stypes.Cons:
        raise SchemeTypeError(f'Argument must be a pair')
    return pair.car

@globalfunc('cdr')
def _(pair):
    if type(pair) is not stypes.Cons:
        raise SchemeTypeError(f'Argument must be a pair')
    return pair.cdr
