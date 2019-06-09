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

def check_num(arg, funcname):
    if type(arg) is not stypes.Number:
        raise SchemeTypeError(f'Error while evaluating {funcname}: '
                              f'the argument is not a number')

    
def check_nums(args, funcname):
    for i, arg in enumerate(args, 1):
        if type(arg) is not stypes.Number:
            raise SchemeTypeError(f'Error while evaluating {funcname}: '
                                  f'argument at position {i} is not a number.')


@globalfunc('+')
def _(*args):
    check_nums(args, '+')
    return sum(args, stypes.Number(0))


@globalfunc('-')
def _(*args):
    check_nums(args, '-')
    
    if not args:
        raise SchemeArityError('called - without arguments')

    if len(args) == 1:
        return -args[0]

    itr = iter(args)
    first = next(itr)
    return functools.reduce(operator.sub, itr, first)


@globalfunc('*')
def _(*args):
    check_nums(args, '*')
    return functools.reduce(operator.mul, args, stypes.Number(1))


@globalfunc('/')
def _(a, b):
    check_nums([a, b], '/')
    return a / b


@globalfunc('sub1')
def _(x):
    check_num(x)
    return x - stypes.Number(1)


@globalfunc('add1')
def _(x):
    check_num(x)
    return x + stypes.Number(1)


def create_cmps():
    # All comparison functions are alike; this script creates them all.  It is called
    # right after this definition, this is only to encapsulate the code.
    
    cmp_operators = {'<': operator.lt, '<=': operator.le,
                     '>': operator.gt, '>=': operator.ge}

    def create(operator_name):
        cmp_operator = cmp_operators[operator_name]
        
        @globalfunc(operator_name)
        def _(*args):
            check_nums(args, operator_name)

            if not args:
                return stypes.true

            last = args[0]

            for num in itertools.islice(args, 1, len(args)):
                #print(f'last = {last}, num = {num}, name = {name}, result = {cmp_operator(last, num)}')
                if not cmp_operator(last, num):
                    return stypes.false
                last = num

            return stypes.true
        
    for operator_name in cmp_operators:
        create(operator_name)
        
create_cmps()


@globalfunc('=')
def _(*args):
    check_nums(args, '=')
    
    if not args:
        return stypes.true
    
    itr = iter(args)
    first = next(itr)
    for num in itr:
        if first != num:
            return stypes.false
    return stypes.true


@globalfunc('abs')
def _(num):
    check_num(num, 'abs')
    return stypes.Number(abs(num.pynum))


@globalfunc('square')
def _(num):
    check_num(num, 'square')
    return stypes.Number(num.pynum ** 2)


################################################################################
# pairs. TODO: map, fold, reduce...

def check_pair(x, funcname):
    if type(x) is not stypes.Cons:
        raise SchemeTypeError(f'Error while evaluating {funcname}: '
                              'argument must be a pair.')



@globalfunc('cons')
def _(a, b):
    return stypes.Cons(a, b)


@globalfunc('car')
def _(pair):
    check_pair(pair)
    return pair.car


@globalfunc('cdr')
def _(pair):
    check_pair(pair)
    return pair.cdr

################################################################################
# general. TODO: equal?, eq?, apply

