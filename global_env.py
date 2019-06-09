"""All of the functions in the global environment are defined here"""

import functools
import operator
import itertools

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

@globalfunc('+')
def _(*args):
    result = stypes.Number(0)
    for i, num in enumerate(args):
        if type(num) is not stypes.Number:
            raise SchemeTypeError(f'all arguments to + must be numbers, '
                                  f'but was given a {type(num)} at {i}')
        result += num
    return result

@globalfunc('-')
def _(*args):
    result = stypes.Number(0)
    for i, num in enumerate(args):
        if type(num) is not stypes.Number:
            raise SchemeTypeError(f'all arguments to - must be numbers, '
                                  f'but was given a {type(num)} at {i}')
        result -= num
    return result


@globalfunc('*')
def _(*args):
    result = stypes.Number(1)
    for i, num in enumerate(args):
        if type(num) is not stypes.Number:
            raise SchemeTypeError(f'all arguments to * must be numbers, '
                                  f'but was given a {type(num)} at {i}')
        result *= num
    return result


@globalfunc('/')
def _(a, b):
    if type(a) is not stypes.Number:
        raise SchemeTypeError(f'first argument is not a number')
    if type(a) is not stypes.Number:
        raise SchemeTypeError(f'second argument is not a number')
    return a / b


@globalfunc('sub1')
def _(x):
    if type(x) is not stypes.Number:
        raise SchemeTypeError(f'argument is not a number')
    return x - stypes.Number(1)


@globalfunc('add1')
def _(x):
    if type(x) is not stypes.Number:
        raise SchemeTypeError(f'argument is not a number')    
    return x + stypes.Number(1)


@globalfunc('=')
def _(*args):
    if not args:
        return stypes.true

    def check(num, i):
        if type(num) is not stypes.Number:
            raise SchemeTypeError(f'All arguments should be numbers, '
                                  'but was given a {type(num)} at {i}.')
    
    if len(args) == 2:
        # optimize for the common case
        n1, n2 = args
        check(n1, 1), check(n2, 2)
        return stypes.Boolean.from_bool(n1 == n2)

    itr = iter(args)
    first = next(itr)
    check(first, 1)
    for i, num in enumerate(itr, 2):
        check(num, i)
        if first != num:
            return stypes.false
    return stypes.true


@globalfunc('abs')
def _(num):
    if type(num) is not stypes.SchemeNumber:
        raise SchemeTypeError(f'argument to abs must be a number')
    return stypes.SchemeNumber(abs(num.pynum))


@globalfunc('square')
def _(num):
    if type(num) is not stypes.SchemeNumber:
        raise SchemeTypeError(f'argument to square must be a number')
    return stypes.SchemeNumber(num.pynum ** 2)

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

################################################################################
# general. TODO: equal?, eq?

