'''
* questions:
should the interpreter have a global environment as an attribute?
- i will implement it so that it does have a global environment as an attribute,
  but i am not sure this is the best choice. 
'''

import compiler
import reader

class Interpreter:
    # attributes: self.frame_stack, self.global_env
    # each Interpreter instance starts out with an empty frame stack
    
    def interpret(self, expr_str):
        # evaluate(compile(read(expr_str)), self.global_env)
        self.evaluate(compiler.compile(reader.read(expr_str)))
        
