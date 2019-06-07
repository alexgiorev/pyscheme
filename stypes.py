class SchemeValue:
    '''Base class for all scheme types. Useful for checking if an
    object is a scheme object'''
    pass

class Symbol(SchemeValue):
    """
    Symbols are interned.

    * attributes
    - self._chars: a string of the characters of the symbol
    """

    # _interned_symbols maps strings to Symbol objects which have the
    # same characters as the string
    _interned_symbols = {}
    
    @staticmethod
    def from_str(astr):
        """Returns the symbol with the same letters as @astr"""
        symbol = Symbol._interned_symbols.get(astr)
        
        if symbol is None:
            newsymbol = Symbol.__new__(Symbol)
            newsymbol.chars = astr
            Symbol._interned_symbols[astr] = newsymbol
            return newsymbol

        return symbol

    def __repr__(self):
        return self.chars
        

class Number(SchemeValue):
    """
    Represents a Scheme number. This includes only integers and
    fractions for now.

    * attributes
    - self._pynum: either an int or a Fraction.
    """
    
    @staticmethod
    def from_pynum(pynum):
        """
        @pynum must be an int or a Fraction (what if it
        isn't?). Returns the scheme number having the same value as
        pynum.
        """
        result = Number.__new__(Number)
        result.pynum = pynum
        return result

    def __repr__(self):
        return str(self.pynum)

class String(SchemeValue):
    """
    * attributes
    - self.chars: a python string which represents the characters of the string
    """
    
    @staticmethod
    def from_str(astr):
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
                
        result = String.__new__(String)
        result.chars = ''.join(chars)
        return result
                        

    def __repr__(self):
        return f'"{self.chars}"'

    
class Boolean(SchemeValue):
    """There are only 2 boolean objects. Constructors return those
    objects, they don't create new ones."""

    # holds the actual boolean objects; is filled with values after
    # the class statement. Maps python booleans to the scheme booleans.
    # {True: <the scheme true value>, False: <the scheme false value>}
    _objects = {}
    
    @staticmethod
    def from_bool(abool):
        """Returns the Scheme boolean with the same truth value as
        @abool, which must be a python boolean"""
        
        if type(abool) is not bool:
            raise TypeError(f'argument must be of type bool, not {type(abool)}')
        return Boolean._objects[abool]

    def __repr__(self):
        return '#f' if self is Boolean._objects[False] else '#t'

true = Boolean.__new__(Boolean)
false = Boolean.__new__(Boolean)
Boolean._objects[True] = true
Boolean._objects[False] = false


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
        while pair is not nil:
            yield pair.car
            pair = pair.cdr
            if type(pair) is not Cons:
                raise ValueError(f'{self} is not a scheme list')
        
    
    def __str__(self):
        """Invariant: str(cons)[0] == '(' and str(cons)[-1] == ')'"""
        if type(self.cdr) is Cons:
            return f'({str(self.car)} {str(self.cdr)[1:-1]})'
        elif self.cdr is nil:
            return f'({str(self.car)})'
        else:
            return (f'({str(self.car)} . {str(self.cdr)})')

        
class NilType(SchemeValue):
    def __bool__(self):
        return False

    def __str__(self):
        return "'()"
    
nil = NilType()


class UnspecifiedType(SchemeValue):
    def __str__(self):
        return '#!unspecific'

unspecified = UnspecifiedType()


class CompoundProcedure(SchemeValue):
    def __init__(self, params, step, env):
        self.params = params
        self.step = step
        self.env = env

    @property
    def parts(self):
        return (self.params, self.step, self.env)
    
        
class PrimitiveProcedure:
    def __init__(self, proc):
        self.proc = proc
    
    def __call__(self, *operands):
        self.proc(*operands)
    
