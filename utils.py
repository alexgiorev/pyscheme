class Bundle:
    """Makes it easier to pass around and use information about the interpreter."""
    
    def __init__(self, frame_stack, last_value):
        """frame_stack must not be empty"""
        self.frame_stack = frame_stack
        self.frame = frame_stack[-1]
        self.step_stack = self.frame.step_stack
        self.env = self.frame.env
        self.last_value = last_value
