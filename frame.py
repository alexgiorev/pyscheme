class Frame:
    """A Frame contains a step stack and an environment.
    * attributes:
    - self.step_stack
    - self.env
    """
    
    def __init__(self, main_step, env):
        self.step_stack = [main_step]
        self.env = env
