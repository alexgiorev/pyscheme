import compiler
import parser
import global_env

from frame import Frame


class Interpreter:
    """
    * attributes
    ** global_env: the global environment
    ** frame_stack: the frame stack
    ** last_value:
       the value of the last step (may be None if the last step returns no value)
    ** step_stack:
       The step stack of the bottom frame of the frame stack. self.step_stack is
       equivalent to self.frame.step_stack. ValueError is raised if this
       attribute is fetched when the frame stack is empty.
    ** frame:
       The bottom frame on the frame stack. ValueError is raised if this
       attribute is fetched when the frame stack is empty.
    ** env
       The environment of the bottom frame. self.env is equivalent to
       self.frame.env. A ValueError is raised if this attribute is fetched when
       the frame stack is empty.
    """

    def __init__(self):
        self.global_env = global_env.make()
        self.frame_stack = []
        self.last_value = None

        
    @property
    def step_stack(self):
        """Returns the step stack of the bottom frame of the frame stack."""
        
        if not self.frame_stack:
            raise ValueError('the frame stack is empty')
        
        return self.frame_stack[-1].step_stack


    @property
    def frame(self):
        """Returns the bottom frame of the frame stack."""
        
        if not self.frame_stack:
            raise ValueError('the frame stack is empty')

        return self.frame_stack[-1]

    
    @property
    def env(self):
        """Returns the environment of the bottom frame of the frame stack."""
        return self.frame.env

    
    def istr(self, expr_str):
        """Evaluates the expression encoded by @expr_str in the global
        environment and returns it's value."""
        
        slist = parser.parse(expr_str).car
        expr = compiler.compile(slist)
        return self.evaluate(expr)


    def istr_all(self, exprs_str):
        """Evaluates the sequence of expressions encoded by @exprs_str in the
        global environment and returns a list of their values."""
        
        exprs = (compiler.compile(slist) for slist in parser.parse(exprs_str))
        return [self.evaluate(expr) for expr in exprs]

    
    def ifile(self, filename):
        """Interprets the contents of the file at @filename in the global
        environment. Returns the value of the last expression in the file."""
        
        with open(filename) as f:
            text = f.read()
            
        begin_slist = parser.parse_begin(text)
        begin_expr = compiler.compile(begin_slist)
        return self.evaluate(begin_expr)


    def ifile_all(self, filename):
        """Interprets the contents of the file at @filename in the global
        environment. Returns a list of the values of all top-level
        expressions."""

        with open(filename) as f:
            text = f.read()

        return self.istr_all(text)

    
    def evaluate(self, expr):
        """Evaluates the Expr @expr in the global environment and returns it's
        value."""
        
        self.frame_stack = [Frame(expr.main_step, self.global_env)]
        
        # invariant: self.step_stack stack is not empty
        while self.frame_stack:
            step = self.step_stack.pop()
            self.last_value = step(self)
            if not self.step_stack:
                self.frame_stack.pop()
        return self.last_value
