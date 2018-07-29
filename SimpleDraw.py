"""
A Simple drawing class
"""
import cairo_utils as utils


class SimpleDraw:
    """ The barest abstract class for drawing  """

    def __init__(self, ctx, sizeTuple):
        assert(ctx is not None)
        assert(sizeTuple is not None)
        assert(isinstance(sizeTuple, tuple) and len(sizeTuple) == 2)
        self._ctx = ctx
        self._size = sizeTuple


    def draw(self):
        """ Abstract Method that is called to draw to the canvas """
        return
          

