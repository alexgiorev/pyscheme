"""All of the functions in the global environment are defined here"""

import functools
import operator
import itertools

import stypes
import steptools

from stypes import * # for convenience
from environment import Environment
from exceptions import *

namespace = {} # maps symbols to functions

def make():
    return Environment.from_dict(namespace, None)


def bind(name, scheme_obj):
    sym = Symbol.from_str(name)
    namespace[sym] = scheme_obj

    
def globalfunc(varstr):
    def decorator(func):
        bind(varstr, PrimitiveProcedure(func))
        return func
    return decorator

################################################################################
# numeric functions

def check_num(arg, funcname):
    if type(arg) is not Number:
        raise SchemeTypeError(f'Error while evaluating {funcname}: '
                              f'the argument is not a number')

    
def check_nums(args, funcname):
    for i, arg in enumerate(args, 1):
        if type(arg) is not Number:
            raise SchemeTypeError(f'Error while evaluating {funcname}: '
                                  f'argument at position {i} is not a number: {arg}')


@globalfunc('+')
def _(inter, *args):
    check_nums(args, '+')
    return sum(args, Number(0))


@globalfunc('-')
def _(inter, *args):
    check_nums(args, '-')
    
    if not args:
        raise SchemeArityError('called - without arguments')

    if len(args) == 1:
        return -args[0]

    itr = iter(args)
    first = next(itr)
    return functools.reduce(operator.sub, itr, first)


@globalfunc('*')
def _(inter, *args):
    check_nums(args, '*')
    return functools.reduce(operator.mul, args, Number(1))


@globalfunc('/')
def _(inter, a, b):
    check_nums([a, b], '/')
    return a / b


@globalfunc('sub1')
def _(inter, x):
    check_num(x)
    return x - Number(1)


@globalfunc('add1')
def _(inter, x):
    check_num(x)
    return x + Number(1)


def create_cmps():
    # All comparison functions are alike; this script creates them all.  It is called
    # right after this definition, this is only to encapsulate the code.
    
    cmp_operators = {'<': operator.lt, '<=': operator.le,
                     '>': operator.gt, '>=': operator.ge}

    def create(operator_name):
        cmp_operator = cmp_operators[operator_name]
        
        @globalfunc(operator_name)
        def _(inter, *args):
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
def _(inter, *args):
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
def _(inter, num):
    check_num(num, 'abs')
    return Number(abs(num.pynum))


@globalfunc('square')
def _(inter, num):
    check_num(num, 'square')
    return Number(num.pynum ** 2)


@globalfunc('even?')
def _(inter, num):
    check_num(num, 'even?')
    return Boolean(num.is_even)


@globalfunc('odd?')
def _(inter, num):
    check_num(num, 'even?')
    return Boolean(num.is_odd)


################################################################################
# pair and list functions

def check_pair(x, funcname):
    if type(x) is not Cons:
        raise SchemeTypeError(f'Error while evaluating {funcname}: '
                              'argument must be a pair.')

    
bind('nil', stypes.nil)


@globalfunc('cons')
def _(inter, a, b):
    return Cons(a, b)


@globalfunc('car')
def _(inter, pair):
    check_pair(pair)
    return pair.car


@globalfunc('cdr')
def _(inter, pair):
    check_pair(pair)
    return pair.cdr


@globalfunc('list')
def _(inter, *args):
    return Cons.iterable2list(args)


@globalfunc('empty?')
def _(inter, arg):
    return arg is stypes.nil


@globalfunc('filter')
def _(inter, pred, lst):
    def values_handler(inter):
        bool_results = inter.last_value
        return Cons.iterable2list((value for value, include_it in zip(lst, bool_results)
                                   if include_it))
    
    sequencer = steptools.Sequencer(steptools.Caller(pred, [arg]) for arg in lst)
    inter.step_stack.append(values_handler)
    inter.step_stack.append(sequencer)


@globalfunc('map')
def _(inter, func, *lists):
    def values_handler(inter):
        return Cons.iterable2list(inter.last_value)

    sequencer = steptools.Sequencer(steptools.Caller(func, args) for args in zip(*lists))
    inter.step_stack.append(values_handler)
    inter.step_stack.append(sequencer)


@globalfunc('foldl')
def _(inter, func, init, alist):
    values = iter(alist)
    
    def value_handler(inter):
        try:
            value = next(values)
        except StopIteration:
            return inter.last_value

        caller = steptools.Caller(func, (value, inter.last_value))
        inter.step_stack.append(value_handler)
        inter.step_stack.append(caller)

    inter.step_stack.append(value_handler)
    inter.step_stack.append(steptools.Identity(init))


@globalfunc('foldr')
def _(inter, func, init, alist):
    values = reversed(list(alist))
    
    def value_handler(inter):
        try:
            value = next(values)
        except StopIteration:
            return inter.last_value

        caller = steptools.Caller(func, (value, inter.last_value))
        inter.step_stack.append(value_handler)
        inter.step_stack.append(caller)

    inter.step_stack.append(value_handler)
    inter.step_stack.append(steptools.Identity(init))
    
################################################################################

@globalfunc('apply')
def _(inter, func, alist):
    return inter.step_stack.append(steptools.Caller(func, list(alist)))


@globalfunc('eq?')
def _(inter, arg1, arg2):
    return Boolean(arg1 is arg2)


@globalfunc('equal?')
def _(inter, arg1, arg2):
    return Boolean(arg1 == arg2) # delegate to the objects

