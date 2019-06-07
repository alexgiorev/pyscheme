class Environment:
    """A namespace is a mapping from variables (symbols) to scheme objects. An environment
    is a sequence of namespaces."""

    def __init__(self, variables, values, parent):
        raise NotImplementedError
    
    def lookup(self, var):
        raise NotImplementedError

    def set_variable_value(self, var, value):
        raise NotImplementedError

    def define_variable(self, var, value):
        raise NotImplementedError
