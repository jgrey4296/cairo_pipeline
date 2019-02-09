import numpy as np
from scipy.interpolate import interp1d
from numpy.random import random, dirichlet
from itertools import cycle, islice
from noise import pnoise1
import IPython

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

INTERPOLATION = 'cubic'

class BezierRiverOperator(OperatorTemplate):
    """ An operator to create a river """

    def __init__(self, subdiv, width_min=0.03, width_max=0.08,
                 deviance=0.2,segment_min=0.1,segment_max=0.3,
                 bsel_balance=None):
        assert(segment_min <= segment_max)
        super().__init__()
        if bsel_balance is None:
            bsel_balance = np.array([0.5])
        #the number of subdivisions of the main river line
        self.subdiv = subdiv
        #the amount of variation of the river in total
        self.deviance = deviance
        #amount of width of the shores of the river variation
        self.width_range = np.array([width_min, width_max])
        #amount of length variation of segments
        self.segment_range = (segment_min, segment_max)
        #cutoffs for a random number to select
        #bezier type of a subdivision
        self.bsel_balance = bsel_balance

    def is_oneshot(self):
        return True

    def __call__(self, draw=True, override=False):
        self.delta = []

        #get the values to use:
        bbmin, bbmax, mid, lenR, widR, dev = self.setup_values(self.dc.bbox)

        line_points = None
        #choose a pair of sides
        if random() > 0.5:
            line_points = np.array([[mid,bbmax],[mid, bbmin]])
        else:
            line_points = np.array([[bbmin, mid],[bbmax, mid]])
        the_line = Line.newLine(line_points)
        logging.info("The Points: {}".format(line_points))
        logging.info("The Line: {}".format(the_line))
        ratios = dirichlet(np.ones(self.subdiv), size=1)
        logging.info("Ratios: {}".format(ratios))
        subdivs = the_line.ratio_subdivide(ratios, srange=self.segment_range)
        control_points = None

        target = line_points[1]
        current = line_points[0]
        beziers = []

        #no need for a (end-1 -> end) point
        logging.info("Subdivs: {}".format(subdivs))
        flipSide = False
        for p1,p2 in zip(subdivs, subdivs[1:]):
            logging.info("Determining control points for: {} - {}".format(p1,p2))
            #if having more types, would use inspect.signature class for param access
            #choose a bezier type
            typeCount = (np.random.random() > self.bsel_balance).sum()
            mid = get_midpoint(p1,p2)
            bisector = utils.math.get_bisector(p1, p2, r=flipSide)
            flipSide = not flipSide
            seg_line = Line.newLine(np.array([p1,p2]))

            if typeCount == 0:
                #1 cp bezier
                #offset the control point to within the bounding rectangle
                cp = seg_line.destination(r=np.random.random())
                #offset along the bisector
                #bisector = bisector.dot([[0,-1],[-1,0]])
                cp += bisector * (np.random.random() * dev)
                beziers.append((p1,cp,p2))
            else:
                #2 cp bezier
                #get the two points
                cp1 = seg_line.destination(r=np.random.random())
                cp2 = seg_line.destination(r=np.random.random())
                #offset them appropriately
                cp1 += bisector * (np.random.random() * dev)
                cp2 += bisector * (np.random.random() * dev)
                beziers.append((p1, cp1, cp2, p2))



        logging.info("Beziers: {}".format(beziers))

        #Create the lines
        if not draw:
            return self.delta

        vecSampleData = sample_specs.VectorSample({
            "type" : SampleE.VECTOR,
            "vector" : np.array([0.3,0.2], dtype=np.float),
            "distance" : 600,
            "sample_amnt" : 1.5,
            "vec_amnt" : 50,
            'radius' : 3,
            'colour' : np.array([0,1,1,1], dtype=np.float)
        })

        angleSampleData = sample_specs.AngleSample({
            "sample_amnt" : 3,
            "radRange": [1, 1.5],
            "vec_amnt" : 4,
            "distance" : 300,
            "radius" : 4,
            "shuffle" : False,
            "incRange": [0.004,0.008],
            "colour" : np.array([0.5,0.6, 0.2, 0.3]),
            "easing_1" : [3,1, easings.CODOMAIN.FULL, 0]
        })

        circleSampleData = sample_specs.CircleSample({
            "sample_amnt" : 1.5,
            "distance" : 400,
            "vec_amnt" : 100,
            "radius" : 2,
            "shuffle" : True,
            "colour" : np.array([0.2,0.6,0.4,0.1]),
            "easing_1" : [1, 3, easings.CODOMAIN.FULL, 5],
            "easing_2" : [3, 2, easings.CODOMAIN.FULL, 0],
        })

        #Use a specification
        sampleData = angleSampleData
        edges = self.dc.createBezier(beziers,
                                     edata={'river':True,
                                            EdgeE.WIDTH: 1,
                                            EdgeE.SAMPLE : sampleData,
                                            EdgeE.NULL : True
                                     },
                                     vdata={VertE.NULL : True},
                                     single=True)
        self.delta += edges
        return self.delta

    def setup_values(self, bbox):
        """ Get the lengths, widths and deviance values, from
        a passed in bbox """
        bbox_min, bbox_max, bbox_range, mid_way = super().setup_values(bbox)

        lengthRange = (bbox_range * self.segment_range[0], bbox_range * self.segment_range[1])
        widthRange = (bbox_range * self.width_range[0], bbox_range * self.width_range[1])
        devianceAmnt = bbox_range * self.deviance

        return (bbox_min, bbox_max, mid_way, lengthRange, widthRange, devianceAmnt)
