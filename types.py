class Symbol:
    """
    Symbols are interned.
    """
    
    @staticmethod
    def from_str(astr):
        """Returns the symbol with the same letters as @astr"""
        raise NotImplementedError

class Number:
    """
    Represents a Scheme number. This includes only integers and
    fractions for now.

    * attributes
    - self.pynum: either an int or a Fraction.
    """
    
    @staticmethod
    def from_pynum(pynum):
        """
        @pynum must be an int or a Fraction (what if it
        isn't?). Returns the scheme number having the same value as
        pynum.
        """
        raise NotImplementedError

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
