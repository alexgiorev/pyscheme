import functools

from fractions import Fraction

__all__ = []

def importit(cls):
    __all__.append(cls.__name__)
    return cls


@importit
class SchemeValue:
    '''Base class for all scheme types. Useful for checking if an
    object is a scheme object'''
    pass


@importit
class Symbol(SchemeValue):
    """
    Symbols are interned.

    * attributes
    - self._chars: a string of the characters of the symbol
    """

    # _interned_symbols maps strings to Symbol objects which have the
    # same characters as the string
    _interned_symbols = {}

    def __new__(cls, astr):
        """Returns the symbol with the same letters as @astr"""
        
        symbol = Symbol._interned_symbols.get(astr)
        
        if symbol is None:
            newsymbol = object.__new__(Symbol)
            newsymbol.chars = astr
            Symbol._interned_symbols[astr] = newsymbol
            return newsymbol

        return symbol
        
    def __repr__(self):
        return self.chars


@importit    
@functools.total_ordering
class Number(SchemeValue):
    """* attributes
    - self.pynum: a python number."""

    def __init__(self, pynum):
        self.pynum = pynum
    
    def __add__(self, other):
        return Number(self.pynum + other.pynum)

    def __sub__(self, other):
        return Number(self.pynum - other.pynum)
    
    def __mul__(self, other):
        return Number(self.pynum * other.pynum)

    def __truediv__(self, other):
        p1, p2 = self.pynum, other.pynum
        if type(p1) is type(p2) is int:
            return Number(Fraction(p1, p2))
        return Number(self.pynum / other.pynum)

    def __neg__(self):
        return Number(-self.pynum)
    
    def __repr__(self):
        return str(self.pynum)

    def __eq__(self, other):
        return type(self) is type(other) and self.pynum == other.pynum

    def __lt__(self, other):
        return type(self) is type(other) and self.pynum < other.pynum

    @property
    def is_even(self):
        return self.is_int and self.pynum % 2 == 0

    @property
    def is_odd(self):
        return self.is_int and self.pynum % 2 == 1
    
    @property
    def is_int(self):
        return type(self.pynum) is int


@importit    
class String(SchemeValue):
    """
    * attributes
    - self.chars: a python string which represents the characters of the string
    """

    def __init__(self, astr):
        """Converts the python string @astr to a Scheme string having
        the same letters (except that escapes in @astr are actually
        expanded in the resulting scheme string)"""
        
        chars = []
        escapes = {'t': '\t', 'n': '\n', '\\': '\\', '"': '"'}

        i, lenastr = 0, len(astr)
        while i < lenastr:
            char = astr[i]
            if char == '\\':
                if i == len(astr) - 1:
                    chars.append('\\')
                else:
                    next_char = astr[i+1]
                    actual_char = escapes.get(next_char)
                    if actual_char is not None:
                        chars.append(actual_char)
                    else:
                        chars.append('\\')
                    i += 2
            else:
                chars.append(char)
                i += 1
                
        self.chars = ''.join(chars)
        
    
    def __eq__(self, other):
        return type(other) is String and self.chars == other.chars

    
    def __repr__(self):
        return f'"{self.chars}"'


@importit    
class Boolean(SchemeValue):
    """There are only 2 boolean objects. Constructors return those
    objects, they don't create new ones."""

    # holds the actual boolean objects; is filled with values after
    # the class statement. Maps python booleans to the scheme booleans.
    # {True: <the scheme true value>, False: <the scheme false value>}
    _objects = {}

    def __new__(cls, pybool):
        return Boolean._objects[bool(pybool)]
    
    def __repr__(self):
        return '#f' if self is Boolean._objects[False] else '#t'

    def __bool__(self):
        return self is Boolean._objects[True]
    
true = object.__new__(Boolean)
false = object.__new__(Boolean)
Boolean._objects[True] = true
Boolean._objects[False] = false


@importit
class Cons(SchemeValue):
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

        
    @staticmethod
    def iterable2list(iterable):
        """Returns a Scheme list with the same values as the python list @pylist"""
        result = nil

        try:
            rev = reversed(iterable)
        except TypeError:
            # @iterable is not reversible
            rev = reversed(list(iterable))
        
        for value in rev:
            result = Cons(value, result)
        return result


    @staticmethod
    def pytree2scmtree(pytree):
        """@pytree must be a python list or a scheme value."""
        if type(pytree) is list:
            return Cons.iterable2list(map(Cons.pytree2scmtree, pytree))
        else:
            # pytree is a list
            return pytree

        
    @property
    def is_list(self):
        """Returns True only if @self represents a scheme list."""
        current = self
        while True:
            current = current.cdr
            if current is nil:
                return True
            if type(current) is not Cons:
                return False
        

    @property
    def pylist(self):
        """Returns the python list having the same values as @self. If
        @self does not encode a list, a ValueError is raised."""
        return list(self)

    
    def __iter__(self):
        """@self must encode a scheme list for this function to work
        properly. Otherwise, the first time you enter a cdr which is
        not a Cons, a ValueError will be raised."""

        pair = self
        while True:
            yield pair.car
            pair = pair.cdr
            if pair is nil:
                return
            if type(pair) is not Cons:
                raise ValueError(f'{self} is not a scheme list')

            
    @property
    def cadr(self):
        """Assumes self.cdr is a Cons"""
        return self.cdr.car

    
    @property
    def cddr(self):
        """Assumes self.cdr is a Cons"""        
        return self.cdr.cdr

    
    @property
    def caddr(self):
        """Assumes self.cdr and self.cddr are pairs."""
        return self.cdr.cdr.car

    
    def __getitem__(self, index):
        """If @self is a list and 0 <= @index < length of @self, return the object at
        @index. If the index is not valid, raises an IndexError. If @self is not a list,
        raises a ValueError."""

        if index < 0:
            raise IndexError(f'negative index: {index}')

        i = index
        for value in self: # May raise ValueError at some point if @self is not a list
            if i == 0:
                return value
            i -= 1
            
        raise IndexError(f'index too large: {index}')

    
    def __str__(self):
        """Invariant: str(cons)[0] == '(' and str(cons)[-1] == ')'"""
        if type(self.cdr) is Cons:
            return f'({str(self.car)} {str(self.cdr)[1:-1]})'
        elif self.cdr is nil:
            return f'({str(self.car)})'
        else:
            return (f'({str(self.car)} . {str(self.cdr)})')

        
    def __eq__(self, other):
        return (type(other) is type(self)
                and self.car == other.car
                and self.cdr == other.cdr)


class NilType(SchemeValue):
    @property
    def pylist(self):
        return []
    
    def __bool__(self):
        return False

    def __str__(self):
        return "'()"

    def __iter__(self):
        return iter([])
    
nil = NilType()


class UnspecifiedType(SchemeValue):
    def __repr__(self):
        return '#!unspecific'

unspecified = UnspecifiedType()


@importit
class CompoundProcedure(SchemeValue):
    def __init__(self, params, step, env):
        """
        @params must be a list of symbols
        @step must be a step
        @env must be an environment"""
        
        self.params = params
        self.step = step
        self.env = env

    @property
    def parts(self):
        return (self.params, self.step, self.env)
    

@importit    
class PrimitiveProcedure:
    def __init__(self, proc):
        self.proc = proc
    
    def __call__(self, *operands):
        return self.proc(*operands)
    
