class SchemeException(Exception):
    """Base class for all scheme exceptions"""
    pass


class SchemeArityError(SchemeException):
    pass


class SchemeTypeError(SchemeException):
    pass
