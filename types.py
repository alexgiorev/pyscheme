class Symbol:
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
    raise NotImplementedError
