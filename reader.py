import string
import re

import types

from fractions import Fraction

def read(expr_str):
    """transforms the string @expr_str to a scheme data structure"""
    raise NotImplementedError    

# ======================================================================
# * tokenization.
# TODO: think about a better way of encapsulating this

# ** tokens:
# a token in this context (contrary to it's normal meaning as a
# string) is considered to be an instance of one of {types.Number,
# types.Symbol, types.String, types.Boolean} or a parenthesis string

# ** extraction functions:
# They all take non-empty strings as arguments.  They extract the
# token from the beginning substring and return the rest of the string
# (i.e. the unused part). For example, extract_number("123abc") will
# return (SchemeNumber(123), "abc"). If a token cannot be extracted,
# None is returned. Be careful when calling extraction functions with
# strings that begin with whitespace! They will return None in that
# case.

extraction_funcs = []

def extraction_func(func):
    """decorate all functions which are extraction functions with this"""
    extraction_funcs.append(func)
    return func


@extraction_func
def extract_parenthesis(expr_str):
    first_char = expr_str[0]
    return (first_char, expr_str[1:]) if first_char in "()" else None


@extraction_func
def extract_symbol(expr_str):
    """
    A symbol has the same syntax as a python identifier: starts with a
    letter or '_' and has only alphanumerics afterwards. I know this
    is not normal scheme symbol syntax, and I may fix this later.
    """
    
    if expr_str[0] not in string.ascii_letters + '_':
        return None
    
    for i, char in enumerate(expr_str):
        if not char.isalnum():
            return (types.Symbol.from_str(expr_str[i]),
                    expr_str[i:])
    else:
        # the whole string is an identifier
        return (types.Symbol.from_str(expr_str), '')
        
    
@extraction_func
def extract_number(expr_str):
    """
    syntax:
    <number> := <int>|<frac>
    <int> := (+|-)?<digit>+
    <frac> := (+|-)?<digit>+/<digit>+
    """
    
    number_regex = r'(\+|-)?(\d+)(/\d+)?'
    m = re.match(number_regex, expr_str)
    
    if not m:
        return None
    
    try:
        pynum = int(m.group())
    except ValueError:
        # the matched string cannot be converted to an int
        pynum = Fraction(m.group())

    return (types.Number.from_pynum(pynum), expr_str[m.end():])


@extraction_func
def extract_string(expr_str):
    def ending_dquote_index():
        for i, char in enumerate(expr_str[1:], 1):
            if char == '"' and expr_str[i-1] != '\\':
                return i
        return None

    if expr_str[0] != '"':
        return None

    edqi = ending_dquote_index()
    if edqi is None:
        return None
    else:
        chars = expr_str[1:edqi]
        return (types.String.from_str(chars), expr_str[edqi+1:])


@extraction_func
def extract_boolean(expr_str):
    """ syntax: #t|#f """
    
    if len(expr_str) < 2:
        return None

    first2 = expr_str[:2]
    
    if first2 == '#t':
        return (types.Boolean.from_bool(True), expr_str[2:])
    elif first2 == '#f':
        return (types.Boolean.from_bool(False), expr_str[2:])
    else:
        return None


def tokenize(expr_str):
    """
    Returns a list of tokens.
    Raises a ValueError if parsing @expr_str to a list of tokens is not possible.
    """
    
    tokens = [] # will return this
    expr_str = expr_str.lstrip()
    while expr_str:
        for func in token_funcs:
            res = func(expr_str)
            if res is not None:
                token, rest = res
                tokens.append(token)
                expr_str = rest.lstrip()
                break
        else:
            # none of the functions in token_funcs was able to
            # extract a token from expr_str, so raise a ValueError
            raise ValueError(f'unable to extract a token from {expr_str}')
    return tokens
