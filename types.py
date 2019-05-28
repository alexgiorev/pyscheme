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

    def __str__(self):
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

    def __str__(self):
        return str(self.pynum)

class String:
    @staticmethod
    def from_str(astr):
        """Converts the python string @astr to a Scheme string. If
        @astr contains escape sequences, they are expanded"""
        raise NotImplementedError

class Boolean:
    """There are only 2 boolean objects. Constructors return those
    objects, they don't create new ones."""
    
    @staticmethod
    def from_bool(abool):
        """Returns the Scheme boolean with the same truth value as
        @abool, which must be a python boolean"""
        raise NotImplementedError
