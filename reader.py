import string
import re

import stypes

from fractions import Fraction

def read(expr_str):
    """transforms the string @expr_str to a scheme data structure"""
    raise NotImplementedError    

"""
================================================================================

* tokenization.
TODO: think about a better way of encapsulating this

** tokens:
a token in this context (contrary to it's normal meaning as a string)
is considered to be an instance of one of {stypes.Number, stypes.Symbol,
stypes.String, stypes.Boolean} or a parenthesis string

** extraction functions:
They all take non-empty strings as arguments.  They extract the token
from the beginning substring and return the rest of the string
(i.e. the unused part). For example, extract_number("123abc") will
return (SchemeNumber(123), "abc"). If a token cannot be extracted,
None is returned. Be careful when calling extraction functions with
strings that begin with whitespace! They will return None in that
case.
"""

extraction_funcs = []

def extraction_func(func):
    """decorate all functions which are extraction functions with this"""
    extraction_funcs.append(func)
    return func


@extraction_func
def extract_parenthesis(expr_str):
    first_char = expr_str[0]
    return (first_char, expr_str[1:]) if first_char in "()" else None

# used by extract_symbol and extract_number
_number_regex = r'(\+|-)?(\d+)(/\d+)?'

@extraction_func
def extract_symbol(expr_str):
    """
    A symbol literal a sequence of characters from {<letters> <digits>
    ! $ % & * / : < = > ? ~ _ ^} that cannot be interpreted as a
    number.  So 123 is not a symbol literal, even though it is a
    sequence of the above characters.
    """

    charset = '[-+.!A-Za-z0-9!$%&*/:<=>?~_^]'

    m = re.match(f'{charset}+', expr_str)

    if m:
        astr = m.group()
        if re.match(f'{_number_regex}$', astr):
            return None
        rest = expr_str[m.end():]
        return (stypes.Symbol.from_str(astr), rest)
    else:
        return None
        
    
@extraction_func
def extract_number(expr_str):
    """
    syntax:
    <number> := <int>|<frac>
    <int> := (+|-)?<digit>+
    <frac> := (+|-)?<digit>+/<digit>+
    """
    
    m = re.match(_number_regex, expr_str)
    
    if not m:
        return None
    
    try:
        pynum = int(m.group())
    except ValueError:
        # the matched string cannot be converted to an int
        pynum = Fraction(m.group())

    return (stypes.Number.from_pynum(pynum), expr_str[m.end():])


@extraction_func
def extract_string(expr_str):
    """
    syntax of string literals: a sequence of characters enclosed in
    double quotes, with there being no backlash before the last double
    quote. The double quotes are part of the literal, but will not be
    a part of the resulting string object. For example, the literal
    "abc\"def" denotes the string which has the characters {a, b, c,
    ", d, e, f}.
    """
    
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
        return (stypes.String.from_str(chars), expr_str[edqi+1:])


@extraction_func
def extract_boolean(expr_str):
    """ syntax: #t|#f """
    
    if len(expr_str) < 2:
        return None

    first2 = expr_str[:2]
    
    if first2 == '#t':
        return (stypes.Boolean.from_bool(True), expr_str[2:])
    elif first2 == '#f':
        return (stypes.Boolean.from_bool(False), expr_str[2:])
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
        for func in extraction_funcs:
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
