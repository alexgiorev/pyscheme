class Symbol:
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
        return f"'{self.chars}"
        

class Number:
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

class String:
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

    
class Boolean:
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

Boolean._objects[False] = Boolean.__new__(Boolean)
Boolean._objects[True] = Boolean.__new__(Boolean)
