"""
An adaptation of Tidal's approach to time.
Patterns are cycles, with positions described using rational numbers,
to avoid floating point issues
"""
from fractions import Fraction as f

class RationalTime
    """ Tidal-style rational number approach to time and patterns """

    def __init__(self, fps):
        self.current_position = 0
        #used to create the base fractional time steps:
        self.fps = fps
        #the timestep array
        self.base = [(f(x, self.fps), 'step') for x in range(self.fps)]
        self.patterns = []

    def add_pattern(self, *args):
        """ Add lists of fraction tuples to the timeline """
        self.patterns += args

    def step(self):
        self.current_position += 1
        if self.current_position >= self.fps:
            self.current_position = 0

    def get_current(self):
        
