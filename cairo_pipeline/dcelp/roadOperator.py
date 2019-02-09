import numpy as np
import IPython
from itertools import cycle, islice
from noise import pnoise1
from cairo_utils.dcel.constants import VertE, EdgeE, FaceE, SampleE
from cairo_utils.constants import QUARTERPI, TWOPI
from cairo_utils.dcel.Line import Line
import cairo_utils.dcel.sample_specs as sample_specs
from cairo_utils.math import bezier1cp, bezier2cp, get_midpoint
from cairo_utils import easings
import cairo_utils as utils
from . import heightmap
from .operatorTemplate import OperatorTemplate
import logging as root_logger
logging = root_logger.getLogger(__name__)


AMNT = 10

class RoadOperator(OperatorTemplate):
    """ Operator to create a road, ignoring intersections
    Potential Growth Rules:  (*: selected)
    Random *
    Growth
    Cul de Sac
    Hole Closing
    Island Connecting
    Terrain Following
    Shape Laying
    Wheel
    Face Exploration
    Edge exploration and return
    """

    def __init__(self, minMaxWidth, minMaxLength, amnt=AMNT, hbal=0.5, hbounds=None):
        super().__init__()
        self.minMaxWidth = minMaxWidth
        self.minMaxLength = minMaxLength
        self.useCount = 0
        self.targetAmnt = amnt
        self.hbal = hbal
        self.hbounds = hbounds

        if self.hbounds is None:
            self.hbounds = [200,500]

    def operate(self, draw=True, override=False):
        """ Performs the operator, returns all changes as a list """
        self.delta = []
        edges = []
        maxmin, ranges, mids = super().setup_values(self.dc.bbox)

        if np.random.random() > self.hbal:
            #Choose two random points and draw
            ps = np.random.random((2,2)) * ranges
            v1, v2 = [self.dc.newVertex(x) for x in ps]
            edges.append(self.dc.newEdge(v1, v2, edata={"road" : True,
                                                        EdgeE.TEXT : True}))
        else:
            #or make a horizontal line
            rLen = self.hbounds[0] + (np.random.random() * (self.hbounds[1] - self.hbounds[0]))
            amnt = np.array([rLen,0])
            pos = (maxmin[:,0] + amnt) + (np.random.random((2,)) * (maxmin[:,1] - amnt))
            edges.append(self.dc.createEdge(pos, pos + amnt, edata={"road":True,EdgeE.TEXT: True}))


        self.delta += edges
        return self.delta

    def is_oneshot(self):
        if self.useCount < self.targetAmnt:
            return False
        return True

    def __exit__(self, type, value, traceback):
        super().__exit__(type,value,traceback)
        if type is None:
            self.useCount += 1


    def unwind(self):
        self.dc.purge(targets=self.delta)
        self.delta = []
