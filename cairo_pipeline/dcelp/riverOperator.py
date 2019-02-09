import numpy as np
from scipy.interpolate import interp1d
from numpy.random import random
from noise import pnoise1
import IPython

from cairo_utils.dcel.constants import VertE, EdgeE, FaceE
from cairo_utils.constants import QUARTERPI, TWOPI
from cairo_utils.dcel.Line import Line
import cairo_utils as utils
from . import heightmap
from .operatorTemplate import OperatorTemplate
import logging as root_logger
logging = root_logger.getLogger(__name__)

INTERPOLATION = 'cubic'

class RiverOperator(OperatorTemplate):
    """ An operator to create a river """

    def __init__(self, subdiv, octaves=1, width_min=0.03, width_max=0.08,
                 deviance=0.2, repeats=3, tolerance=0.1, max_rot_delta=0.1):
        #the number of subdivisions of the main river line
        self.subdiv = subdiv
        #octaves of the perlin noise
        self.octaves = octaves
        self.deviance = deviance
        self.repeats = repeats
        #the proportion of internal steps that it takes before vector correction
        self.tolerance = tolerance

        self.width_range = np.array([width_min, width_max])

        #Required:
        self.delta = []
        self.dc = None
        self.i = None

    def is_oneshot(self):
        return True

    def __enter__(self):
        logging.info("Entering RiverTick Context")


    def __exit__(self, type, value, traceback):
        logging.info("Exiting RiverTick Context")
        if value is not None:
            logging.warning("Unwinding")
            self.unwind()
        self.dc = None
        self.i = None
        self.delta = []
        #if exiting with an error,
        #undo the operations

    def __call__(self, draw=True, override=False):
        self.delta = []

        #pick a start and end point on two opposite edges
        bbox_min = self.dc.bbox[0]
        bbox_max = self.dc.bbox[2]
        mid_way = int(self.dc.bbox[2] * 0.5)
        line_points = None
        #choose a pair of sides
        if random() > 0.5:
            line_points = np.array([[mid_way,bbox_max],[mid_way, bbox_min]])
        else:
            line_points = np.array([[bbox_min, mid_way],[bbox_max, mid_way]])
        the_line = Line.newLine(line_points)
        subdivs = the_line.subdivide(self.subdiv)
        bisector = utils.math.get_bisector(*line_points)

        target = line_points[1]
        current = line_points[0]

        halfPoints = int((self.subdiv + 2) * 0.5)
        easing = pow(np.cos(QUARTERPI * np.linspace(-1, 1, halfPoints)), 3.5).reshape((-1,1))
        rotAmnt = np.array([(TWOPI * 1.3) * pnoise1(x * 0.001, octaves=self.octaves, base=int(random()*1000)) for x in range(halfPoints)])
        rotAmnt -= rotAmnt.mean()
        rot = np.column_stack((np.cos(rotAmnt), np.sin(rotAmnt))) * easing
        smoothedRot = utils.math._interpolate(rot, halfPoints * 2)
        devianceAmnt = self.deviance * self.dc.bbox[2]
        final_points = subdivs + (smoothedRot * devianceAmnt)


        #Create the lines
        if not draw:
            return self.delta

        edges = self.dc.createPath(final_points, edata={'river':True,
                                                        EdgeE.WIDTH: 1})
        self.delta += edges
        return self.delta

    def unwind(self):
        self.dc.purge(targets=self.delta)
        self.delta = []
