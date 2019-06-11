import compiler
import parser
import global_env

from frame import Frame


class Interpreter:
    """attributes: self.global_env"""

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
        """Evaluates @expr_str in the global environment."""
        slist = parser.parse(expr_str).car
        expr = compiler.compile(slist)
        return self.evaluate(expr)

    
    def ifile(self, filename):
        """Interprets the contents of the file at @filename in the global environment."""
        with open(filename) as f:
            text = f.read()
            
        begin_slist = parser.parse_begin(text)
        begin_expr = compiler.compile(begin_slist)
        return self.evaluate(begin_expr)

    
    def evaluate(self, expr):
        """Evaluates the Expr @expr in the global environment."""
        
        self.frame_stack = [Frame(expr.main_step, self.global_env)]
        
        # invariant: self.step_stack stack is not empty
        while self.frame_stack:
            step = self.step_stack.pop()
            self.last_value = step(self)
            if not self.step_stack:
                self.frame_stack.pop()
        return self.last_value

i = Interpreter()
