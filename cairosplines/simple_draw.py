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
        # [p1, cp1, cp2, p2]
        self._beziers = np.zeros(8)
        # [p, min_radius, max_radius, min_rads, max_rads]
        self._circles = np.zeros(6)
        #additional data
        self._samples = np.zeros(2)
        self._text = []

    #------------------------------
    # def Abstract Methods
    #------------------------------

    def draw(self, bbox=None):
        """ Abstract Method that is called to draw to the canvas """
        raise Exception("Abstract Draw needs to be implemented")

    def iterate(self, i, data):
        """ Abstract method called to increment the state of a drawing """
        return []

    def generate(self):
        """ Abstract Method called to generate the drawing data """
        raise Exception("Abstract Generate needs to be implemented")

	#------------------------------
	# def Draw Primitives
	#------------------------------

    def add_points(self, points):
        """ Add 2 dimensional points to the data to draw """
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == 2)
        self._core_verts = np.row_stack((self._core_verts, points))

    def add_lines(self, lines):
        """ Add lines to sample then draw """
        assert(isinstance(lines, np.ndarray))
        assert(lines.shape[1] == 4)
        self._lines = np.row_stack((self._lines, lines))

    def add_bezier(self, beziers):
        """ Add 2 cp bezier curves to sample then draw """
        assert(isinstance(beziers, np.ndarray))
        assert(beziers.shape[1] == 8)
        self._beziers = np.row_stack((self._beziers, beziers))

    def add_circle(self, circles):
        """ Add circles to sample then draw """
        assert(isinstance(circles, np.ndarray))
        assert(circles.shape[1] == 6)
        self._circles = np.row_stack((self._circles, circles))

    def add_text(self, text, position, size, colour):
        """ Adds text on top of the drawing """
        self._text.append((text,position,size, colour))

    #------------------------------
    # def Implemented Drawing:
    #------------------------------

    def draw_text(self):
        for (t,p,s,c) in self._text:
            self._ctx.set_font_size(s)
            self._ctx.set_source_rgba(*c)
            utils.drawing.drawText(self._ctx, p, t)

    def draw_complex(self, colour=None, bbox=None, push=False):
        """ A Wrapper for Draw, simplifies stack management and clearing """
        if push:
            self._ctx.save()
        if colour is not None:
            utils.drawing.clear_canvas(self._ctx, colour=colour, bbox=bbox)
        self.draw(bbox)
        if push:
            self._ctx.restore()

    def start_iterate(self, n):
        """ Iterates the class a number of times """
        data = []
        for x in range(n):
            data = self.iterate(x, data)

	#------------------------------
    # def Sampling
    #------------------------------

    def sample_shapes(self, n):
        """ Sample along defined shapes """
        ts = np.linspace(0,1,n)
        #sample lines
        self._samples = np.row_stack((self._samples, utils.math.sampleAlongLine(self._lines, ts)))
        #sample beziers
        self._samples = np.row_stack((self._samples, utils.math.bezier2cp(self._beziers, p=ts)))
        #sample circles - on diameter
        self._samples = np.row_stack((self._samples, utils.math.sampleCircle(self._circles, ts)))
