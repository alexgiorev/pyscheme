import string
import re

import stypes

from stypes import *
from fractions import Fraction


def parse_begin(expr_str):
    slist = parse(expr_str)
    begin = Symbol('begin')
    return Cons(begin, slist)


def parse(expr_str):
    """Transforms the string @expr_str to a list of scheme data
    structures.  Raises a ValueError if parsing @expr_str is not
    possible.  TODO: document in more detail, raise ValueError with
    meaningful messages """

    def remaining_tokens(tokens_iter):
        """Assumes an open parenthesis was encountered and this
        returns an iterator of the tokens up to the closing
        parenthesis. The closing parenthesis is not part of the
        resulting iterator. Raises ValueError if there is no closing
        parenthesis"""
        
        accum = 1
        tokens = []
        for token in tokens_iter:
            if token == '(':
                accum += 1
            elif token == ')':
                accum -= 1
                if accum == 0:
                    return iter(tokens)
            tokens.append(token)
        else:
            # all tokens were exhauseted and no closing parenthesis was found
            raise ValueError(f'no closing parenthesis: {expr_str}')        

    def parse_tokens(tokens_iter):        
        elements = []
        for token in tokens_iter:
            if token == '(':
                elements.append(parse_tokens(remaining_tokens(tokens_iter)))
            elif token == '\'':
                # the loop will end after this block
                rest = parse_tokens(tokens_iter) # exhausts @tokens_iter         
                if not rest:
                    raise ValueError(f'no element after a quote')
                rest[0] = [Symbol('quote'), rest[0]]
                elements.extend(rest)
            elif isinstance(token, SchemeValue):
                elements.append(token)
            else:
                raise ValueError(f'Invalid token (or valid token at '
                                 f'the wrong position): {token}')

        return elements

    pytree = parse_tokens(iter(tokenize(expr_str)))
    return Cons.pytree2scmtree(pytree)

"""
================================================================================

* tokenization.
TODO: think about a better way of encapsulating this

** tokens:
a token in this context (contrary to it's normal meaning as a string)
is considered to be an instance of one of {Number, Symbol,
String, Boolean} or a parenthesis string

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


@extraction_func
def extract_quote(expr_str):
    return ('\'', expr_str[1:]) if expr_str[0] == '\'' else None


@extraction_func
def extract_symbol(expr_str):
    """
    A symbol literal a sequence of characters from {<letters> <digits>
    ! $ % & * / : < = > ? ~ _ ^} that cannot be interpreted as a
    number.  So 123 is not a symbol literal, even though it is a
    sequence of the above characters.
    """

    charset = '[-+.!A-Za-z0-9$%&*/:<=>?~_^]'
    m = re.match(f'{charset}+', expr_str)

    if m:
        astr = m.group()
        
        # if astr is a string that can be interpreted as a number, return None
        num_attempt = extract_number(astr)
        if num_attempt is not None and num_attempt[1] == '':
            # @astr is a number string
            return None
        
        rest = expr_str[m.end():]
        return (Symbol(astr), rest)
    else:
        return None
        
    
@extraction_func
def extract_number(expr_str):
    """
    syntax:
    <number> := <int>|<frac>
    <int> := (+|-)?<digit>+
    <float> := (+|-)?<digit>+.<digit>+
    <frac> := (+|-)?<digit>+/<digit>+
    """
    
    intRE = r'(\+|-)?(\d+)'
    floatRE = r'(\+|-)?(\d+)\.(\d+)'
    fracRE = r'(\+|-)?(\d+)/(\d+)'
    
    def try_re(expr_str, RE, numtype):
        m = re.match(RE, expr_str)
        
        if not m:
            return None

        rest = expr_str[m.end():]
        pynum = numtype(m.group())
        return pynum, rest
    
    for RE, numtype in zip((fracRE, floatRE, intRE), (Fraction, float, int)):
        attempt = try_re(expr_str, RE, numtype)
        if attempt is not None:
            pynum, rest = attempt
            return (Number(pynum), rest)
        
    return None


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
        return (String(chars), expr_str[edqi+1:])


@extraction_func
def extract_boolean(expr_str):
    """ syntax: #t|#f """
    
    if len(expr_str) < 2:
        return None

    first2 = expr_str[:2]
    
    if first2 == '#t':
        return (Boolean(True), expr_str[2:])
    elif first2 == '#f':
        return (Boolean(False), expr_str[2:])
    else:
        return None


def extract_comment(expr_str):
    """@expr_str begins with ';'. Return the rest after extracting the comment"""
    comment_end = expr_str.find('\n')
    if comment_end == -1:
        return ''
    else:
        return expr_str[comment_end + 1:]

    
def tokenize(expr_str):
    """
    Returns a list of tokens.
    Raises a ValueError if parsing @expr_str to a list of tokens is not possible.
    """
    
    tokens = [] # will return this
    expr_str = expr_str.lstrip()
    while expr_str:
        if expr_str[0] == ';':
            expr_str = extract_comment(expr_str)
        else:
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
