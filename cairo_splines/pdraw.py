"""
A Drawing Class that takes a defined pipeline and draws it
"""

import numpy as np
from itertools import islice
import cairo_utils as utils
import IPython
from . import constants

class PDraw:
    """ Draws a Pipeline of operations """

    def __init__(self, ctx, sizeTuple, surface):
        assert(ctx is not None)
        assert(sizeTuple is not None)
        assert(surface is not None)
        assert(isinstance(sizeTuple, tuple) and len(sizeTuple) == 2)
        self._ctx = ctx
        self._surface = surface
        self._size = sizeTuple
        self._center = (sizeTuple[0] * 0.5, sizeTuple[1] * 0.5)
        #Core points : np.array(x,y,rad,r,g,b,a)
        self._core_verts = np.zeros((1,constants.SAMPLE_DATA_LEN))
        #More Complex shapes
        self._lines = np.zeros((1,constants.LINE_DATA_LEN))
        # [p1, cp1, cp2, p2]
        self._beziers = np.zeros((1,constants.BEZIER_DATA_LEN))
        # [p, min_radius, max_radius, min_rads, max_rads]
        self._circles = np.zeros((1,constants.CIRCLE_DATA_LEN))
        #additional data
        self._samples = np.zeros((1,constants.SAMPLE_DATA_LEN))
        self._noise = None
        self._stack = []
        self._text = []
        # Lookup of Objects associated with basic data
        # eg: _nodes['_core_verts'][1] can hold an object associated with _core_verts[0]
        self._nodes = {}
        # Debug flag for layers:
        self._debug= False

    def pipeline(self, pipelines):
        """ Transforms the drawing in a set of steps """
        pipeline_data = {}
        pipe_pairs = zip(islice(pipelines, 0, len(pipelines), 2),
                         islice(pipelines, 1, len(pipelines), 2))
        for (x, opts) in pipe_pairs:
            pipeline_data = x(self, opts, pipeline_data)
        return pipeline_data

    #------------------------------
	# def Draw Primitives
	#------------------------------

    def add_points(self, points):
        """ Add 2 dimensional points to the data to draw,
        points: np.array([[x,y,r,r,g,b,a]])
        """
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == constants.SAMPLE_DATA_LEN)
        self._core_verts = np.row_stack((self._core_verts, points))

    def add_lines(self, lines):
        """ Add lines to sample then draw
        lines: np.array([[x,y,x,y,r,g,b,a]])
        """
        assert(isinstance(lines, np.ndarray))
        assert(lines.shape[1] == constants.LINE_DATA_LEN)
        self._lines = np.row_stack((self._lines, lines))

    def add_bezier(self, beziers):
        """ Add 2 cp bezier curves to sample then draw
        beziers: np.array([[x1,y1,cx1, cy1, cx2, cy2, x2, y2, r, g, b, a]])
        """
        assert(isinstance(beziers, np.ndarray))
        assert(beziers.shape[1] == constants.BEZIER_DATA_LEN)
        self._beziers = np.row_stack((self._beziers, beziers))

    def add_circle(self, circles):
        """ Add circles to sample then draw
        Circles: np.array([[x,y, rad_min, rad_max, radius_min, radius_max,
        r, g, b, a]])
        """
        assert(isinstance(circles, np.ndarray))
        assert(circles.shape[1] == constants.CIRCLE_DATA_LEN)
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
            utils.drawing.draw_text(self._ctx, p, t)


    #------------------------------
    # def Sampling
    #------------------------------

    def sample_shapes(self, n, r=10, types=None):
        """ Sample along defined shapes """
        if types is None:
            types = ['line','bezier','circle']
        if 'line' in types:
            self.sample_lines(n, r=r)
        if 'bezier' in types:
            self.sample_beziers(n, r=r)
        if 'circle' in types:
            self.sample_circles(n, r=r)

    def sample_lines(self, n, r=10):
        #sample lines
        ts = np.linspace(0,1,n)
        if len(self._lines) > 1:
            self._samples = np.row_stack((self._samples,
                                          utils.umath.sample_wrapper(
                                              utils.umath.sample_along_lines,
                                              self._lines[1:,:-constants.COLOUR_SIZE],
                                              ts,
                                              r,
                                              self._lines[1:,-constants.COLOUR_SIZE:])
            ))

    def sample_beziers(self, n, r=10):
        #sample beziers
        ts = np.linspace(0,1,n)
        if len(self._beziers) > 1:
            self._samples = np.row_stack((self._samples,
                                          utils.umath.sample_wrapper(
                                              utils.umath.bezier2cp,
                                              self._beziers[1:,:-constants.COLOUR_SIZE],
                                              n,
                                              r,
                                              self._beziers[1:,-constants.COLOUR_SIZE:])
            ))

    def sample_circles(self, n, r=10):
        #sample circles - on diameter
        ts = np.linspace(0,1,n)
        if len(self._circles) > 1:
            f = lambda x,c: utils.umath.sample_circle(x,c,sort_rads=False, sort_radi=False)
            self._samples = np.row_stack((self._samples,
                                          utils.umath.sample_wrapper(
                                              f,
                                              self._circles[1:,:-constants.COLOUR_SIZE],
                                              n,
                                              r,
                                              self._circles[1:,-constants.COLOUR_SIZE:])
            ))


    #------------------------------
    # def Node Utilities
    #------------------------------
    def lookup(self, group, index, missing=None):
        self.create_group(group)
        if index in self._nodes[group]:
            return self._nodes[group][index]
        if missing is None:
            missing = {}
        if callable(missing):
            missing = missing()
        self._nodes[group][index] = missing
        return missing

    def create_group(self, group):
        if group in self._nodes:
            return
        self._nodes[group] = {}
