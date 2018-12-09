"""
A Simple drawing class
"""
import numpy as np
import cairo_utils as utils


class SimpleDraw:
    """ The barest abstract class for drawing  """

    def __init__(self, ctx, sizeTuple):
        assert(ctx is not None)
        assert(sizeTuple is not None)
        assert(isinstance(sizeTuple, tuple) and len(sizeTuple) == 2)
        self._ctx = ctx
        self._size = sizeTuple
        #Core points
        self._core_verts = np.zeros(2)
        #More Complex shapes
        self._lines = np.zeros(4)
        self._beziers = np.zeros(8)
        self._circles = np.zeros(3)
        #additional data
        self._samples = np.zeros(2)
        self._text = []
        
    def draw(self, bbox=None):
        """ Abstract Method that is called to draw to the canvas """
        raise Exception("Abstract Draw needs to be implemented")

    def iterate(self, i, data):
        raise Exception("Abstract Iterate needs to be implemented")
    	#return []

    def draw_complex(self, colour=None, bbox=None, push=False):
        if push:
            self._ctx.save()
        if colour is not None:
            utils.clear_canvas(self._ctx, colour=colour, bbox=bbox)
        self.draw(bbox)
        if push:
            self._ctx.restore()

    def start_iterate(self, n):
        data = []
        for x in range(n):
            data = self.iterate(x, data)

    def add_points(self, points):
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == 2)
        self._core_verts = np.row_stack(self._core_verts, points)

    def add_lines(self, lines):
        assert(isinstance(lines, np.ndarray))
        assert(lines.shape[1] == 4)
        self._lines = np.row_stack(self._lines, lines)

    def add_bezier(self, beziers):
        assert(isinstance(beziers, np.ndarray))
        assert(beziers.shape[1] == 8)
        self._beziers = np.row_stack(self._beziers, beziers)

    def add_circle(self, circles):
        assert(isinstance(circles, np.ndarray))
        assert(circles.shape[1] == 3)
        self._circles = np.row_stack(self._circles, circles)
        
    
    def add_text(self, text, position, size, colour):
        """ Adds text on top of the drawing """
        self._text.append((text,position,size, colour))

    def draw_text(self):
        for (t,p,s,c) in self._text:
            self._ctx.save()
            self._ctx.set_font_size(s)
            self._ctx.set_source_rgba(*c)
            self._ctx.move_to(*p)
            self._ctx.show_text(t)
            self._ctx.restore()
    
    def sample_shapes(self, n):
        """ Sample along defined shapes """
        #sample lines

        #sample beziers

        #sample circles
