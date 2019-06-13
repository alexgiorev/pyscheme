import stypes

from exceptions import *
from environment import Environment
from frame import Frame


class Sequencer:
    """The result of a Sequencer is a list of the values of it's expressions in the same
    order."""
    
    def __init__(self, steps):
        """@steps must be an iterator of steps."""
        self.steps = steps
        self.result = []

        
    def value_handler(self, inter):
        self.result.append(inter.last_value)
        next_step = next(self.steps, None)
        
        if next_step is None:
            return self.result

        inter.step_stack.append(self.value_handler)
        inter.step_stack.append(next_step)
        
        
    def __call__(self, inter):
        first_step = next(self.steps, None)
        if first_step is None:
            return []
        else:
            inter.step_stack.append(self.value_handler)
            inter.step_stack.append(first_step)
        

class Caller:
    """Returns a step which evaluates a function with a given list of arguments."""

    def __init__(self, func, args):
        self.operator = func
        self.operands = args

        
    def __call__(self, inter):
        operator = self.operator
        operands = self.operands
        
        if type(operator) is stypes.PrimitiveProcedure:
            return operator(inter, *operands)
        elif type(operator) is stypes.CompoundProcedure:
            params, step, env = operator.parts

            if len(params) != len(operands):
                raise SchemeArityError(f'Expected {len(params)} arguments, '
                                       f'but got {len(operands)}.')

            new_env = Environment(params, operands, env)

            if not inter.step_stack: # tail call optimization
                inter.frame_stack.pop()

            inter.frame_stack.append(Frame(step, new_env))
        else:
            raise SchemeTypeError(f'{operator} is not applicable')

        
