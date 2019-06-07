import utils
import compiler
import parser
import global_env

from frame import Frame


class Interpreter:
    """attributes: self.global_env"""

    def __init__(self, global_env):
        self.global_env = global_env
    
    def interpret(self, expr_str):
        """evaluates @expr_str in the global environment"""
        slist = parser.parse(expr_str).car
        expr = compiler.compile(slist)
        return self.evaluate(expr)

    def evaluate(self, expr):
        """evaluates the Expr @expr in the global environment"""
        
        frame_stack = [Frame(expr.main_step, self.global_env)]
        last_value = None
        
        # invariant: frame_stack[-1]'s step stack is not empty
        while frame_stack:
            frame = frame_stack[-1]
            step = frame.step_stack.pop()
            last_value = step(utils.Bundle(frame_stack, last_value))
            if not frame.step_stack:
                frame_stack.pop()
        return last_value

