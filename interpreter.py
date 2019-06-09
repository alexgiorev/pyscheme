import utils
import compiler
import parser
import global_env

from frame import Frame


class Interpreter:
    """attributes: self.global_env"""

    def __init__(self):
        self.global_env = global_env.make()
    
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
        
        frame_stack = [Frame(expr.main_step, self.global_env)]
        last_value = None
        
        # invariant: frame_stack[-1]'s step stack is not empty
        while frame_stack:
            # print(f'frame_stack = {frame_stack}')
            # print(f'step_stack = {frame_stack[-1].step_stack}')
            # print(f'last_value = {last_value}')
            # print()
            step = frame_stack[-1].step_stack.pop()
            last_value = step(utils.Bundle(frame_stack, last_value))
            if not frame_stack[-1].step_stack:
                frame_stack.pop()
        return last_value

i = Interpreter()

