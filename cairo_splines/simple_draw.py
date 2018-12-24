"""
A Simple drawing class
"""
import numpy as np
import cairo_utils as utils
import IPython

class SimpleDraw:
    """ The barest abstract class for drawing  """

    def __init__(self, ctx, sizeTuple):
        assert(ctx is not None)
        assert(sizeTuple is not None)
        assert(isinstance(sizeTuple, tuple) and len(sizeTuple) == 2)
        self._ctx = ctx
        self._size = sizeTuple
        self._center = (sizeTuple[0] * 0.5, sizeTuple[1] * 0.5)
        #Core points : np.array(x,y,rad,r,g,b)
        self._core_verts = np.zeros((1,7))
        #More Complex shapes
        self._lines = np.zeros((1,8))
        # [p1, cp1, cp2, p2]
        self._beziers = np.zeros((1,12))
        # [p, min_radius, max_radius, min_rads, max_rads]
        self._circles = np.zeros((1,10))
        #additional data
        self._samples = np.zeros((1,7))
        self._text = []
        self._initial_conditions = []

    #------------------------------
    # def Abstract Methods
    #------------------------------

    def draw(self, bbox=None):
        """ Abstract Method that is called to draw to the canvas """
        utils.drawing.draw_circle(self._ctx, self._core_verts)
        utils.drawing.draw_circle(self._ctx, self._samples)

    def iterate(self, i, frontier=None):
        """ Abstract method called to increment the state of a drawing """
        return []

    def generate(self):
        """ Abstract Method called to generate the drawing data """
        verts = np.random.random((20,7))
        #scale up the position and radius: ((b - a) * x) + a
        mask = np.array([1,1,1,0,0,0,0], dtype='float64')
        mask *= np.array([self._size[0],self._size[1], self._size[0]*0.01, 0, 0, 0, 0])
        mask += np.array([0,0,0,1,1,1,1])
        points = (verts * mask)
        # self.add_points(points)
        self.add_circle(np.array([[self._center[0], self._center[1],
                                   0, utils.constants.TWOPI,
                                   360, 3800,
                                   0,1,1,0.05
                                   ]]))
        self.add_points(np.array([[self._center[0], self._center[1],300, 1, 0, 0, 1],
                                  [0,0,150, 0, 0, 1,1],
                                  [0,self._size[1],150, 0, 0.5, 0.5, 1],
                                  [self._size[0],0,150, 0.5, 0.5, 0, 1]]))
        self.add_bezier(np.array([[self._center[0] - self._size[0]*0.5, self._center[1],
                                   self._center[0], self._center[1] + self._size[1]*0.25,
                                   self._center[0] + self._size[0]*0.25, self._center[1] - self._size[1]*0.25,
                                  self._center[0] + self._size[0]*0.5, self._center[1],
                                   1,0.2,0.4,1]]))
        self.add_bezier(np.array([[self._center[0] - self._size[0]*0.5, self._center[1],
                                   self._center[0], self._center[1] + self._size[1]*0.25,
                                   self._center[0] + self._size[0]*0.25, self._center[1] - self._size[1]*0.25,
                                  self._center[0] + self._size[0]*0.5, self._center[1],
                                   1,0.2,0.4,1]]))
        self.sample_shapes(800, r=13)
	#------------------------------
	# def Draw Primitives
	#------------------------------

    def add_points(self, points):
        """ Add 2 dimensional points to the data to draw,
        points: np.array([[x,y,r,r,g,b,a]])
        """
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == 7)
        self._core_verts = np.row_stack((self._core_verts, points))

    def add_lines(self, lines):
        """ Add lines to sample then draw
        lines: np.array([[x,y,x,y,r,g,b,a]])
        """
        assert(isinstance(lines, np.ndarray))
        assert(lines.shape[1] == 8)
        self._lines = np.row_stack((self._lines, lines))

    def add_bezier(self, beziers):
        """ Add 2 cp bezier curves to sample then draw
        beziers: np.array([[x1,y1,cx1, cy1, cx2, cy2, x2, y2, r, g, b, a]])
        """
        assert(isinstance(beziers, np.ndarray))
        assert(beziers.shape[1] == 12)
        self._beziers = np.row_stack((self._beziers, beziers))

    def add_circle(self, circles):
        """ Add circles to sample then draw
        Circles: np.array([[x,y, rad_min, rad_max, radius_min, radius_max,
        r, g, b, a]])
        """
        assert(isinstance(circles, np.ndarray))
        assert(circles.shape[1] == 10)
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
        data = self._initial_conditions
        for x in range(n):
            data = self.iterate(x, data)

	#------------------------------
    # def Sampling
    #------------------------------

    def sample_shapes(self, n, r=10):
        """ Sample along defined shapes """
        ts = np.linspace(0,1,n)
        #sample lines
        if len(self._lines) > 1:
            self._samples = np.row_stack((self._samples,
                                          utils.umath.sample_wrapper(
                                              utils.umath.sample_along_lines,
                                              self._lines[1:,:-4],
                                              ts,
                                              r,
                                              self._lines[1:,-4:])
            ))

        #sample beziers
        if len(self._beziers) > 1:
            self._samples = np.row_stack((self._samples,
                                          utils.umath.sample_wrapper(
                                              utils.umath.bezier2cp,
                                              self._beziers[1:,:-4],
                                              n,
                                              r,
                                              self._beziers[1:,-4:])
            ))

        #sample circles - on diameter
        if len(self._circles) > 1:
            f = lambda x,c: utils.umath.sample_circle(x,c,sort_rads=False, sort_radi=False)
            self._samples = np.row_stack((self._samples,
                                          utils.umath.sample_wrapper(
                                              f,
                                              self._circles[1:,:-4],
                                              n,
                                              r,
                                              self._circles[1:,-4:])
            ))
