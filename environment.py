class Environment:
    def __init__(self, variables, values, parent):
        """
        @variables must be an iterable of variables
        @values must be an iterable. (most commonly scheme objects)
        @parent must be an Environment or None
        """
        
        self.namespace = dict(zip(variables, values))
        self.parent = parent

    @staticmethod
    def from_dict(dct, parent):
        """
        @dct must be a dict mapping symbols to scheme values.
        @parent must be an Environment or None.
        """
        result = Environment.__new__(Environment)
        result.namespace = dct.copy()
        result.parent = parent
        return result
        
    def lookup(self, var):
        """returns the value corresponding to @var in @self if @var is not bound in @self,
        raises a LookupError"""
        
        namespace = self.first_namespace_that_binds_the_var(var)
        if namespace is None:
            raise LookupError(f'the variable "{var}" is not bound in this environment')
        return namespace[var]

    def set_variable_value(self, var, value):
        """if @var is bound in @self, changes it's corresponding value to @value
        otherwise, a LookupError is raised"""
        
        namespace = self.first_namespace_that_binds_the_var(var)
        if namespace is None:
            raise LookupError(f'cannot set the variable "{var}" to the value {value}: '
                              'the variable is not bound in the current environment')
        namespace[var] = value

    def define_variable(self, var, value):
        """if @var is bound in @self's namespace, rebinds it to @value
        otherwise, creates a new binding var -> value"""
        self.namespace[var] = value
        
    def __iter__(self):
        current_env = self
        while current_env:
            yield current_env
            current_env = current_env.parent
    
    def first_namespace_that_binds_the_var(self, var):
        for current_env in self:
            if var in current_env.namespace:
                return current_env.namespace
        return None
