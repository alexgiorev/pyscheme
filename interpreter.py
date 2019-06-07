'''
* questions:
- should the interpreter have a global environment as an attribute?
-- i will implement it so that it does have a global environment as an attribute,
  but i am not sure this is the best choice. 
'''

import compiler
import parser
        
class Bundle:
    """Makes it easier to pass around and use information about the interpreter"""
    
    def __init__(self, frame_stack, last_value):
        # frame_stack must not be empty
        self.frame_stack = frame_stack
        self.frame = frame_stack[-1]
        self.step_stack = frame.step_stack
        self.env = frame.env
        self.last_value = last_value
        
class Interpreter:
    # attributes: self.global_env
    
    def interpret(self, expr_str):
        # evaluates @expr_str in the global environment
        self.evaluate(compiler.compile(parser.parse(expr_str)))

    def evaluate(self, expr):
        # evaluates the Expr @expr in the global environment
        
        frame_stack = [Frame(expr.step, self.global_env)]
        last_value = None
        
        # invariant: frame_stack[-1]'s step stack is not empty
        while frame_stack:
            step = frame_stack[-1].step_stack.pop()
            last_value = step(Bundle(frame_stack, last_value))
            if not frame.step_stack:
                frame_stack.pop()
        return last_value


