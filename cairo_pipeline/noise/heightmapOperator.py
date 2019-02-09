import numpy as np

from cairo_utils.dcel.constants import VertE, EdgeE, FaceE
import cairo_utils as utils
from . import heightmap
from .operatorTemplate import OperatorTemplate
import logging as root_logger
logging = root_logger.getLogger(__name__)


class HeightmapOperator(OperatorTemplate):
    """ Operator to Generate a Heightmap """


    def __init__(self, size, subdiv, minheight, layers, octaves, radius):
        self.size = size
        self.subdiv = subdiv
        self.minheight = minheight
        self.layers = layers
        self.octaves = octaves
        self.radius = radius
        self.repeatx = 1000
        self.repeaty = 1000
        self.base = 2.0
        self.delta = []
        self.dc = None
        self.i = None

    def is_oneshot(self):
        return True

    def __enter__(self):
        logging.info("Entering Heightmap Context")


    def __exit__(self, type, value, traceback):
        logging.info("Exiting Heightmap Context")
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
        if not override and 'heightmap' in self.dc.data:
            return self.delta

        hm, qhm, edges = heightmap.gen_heightmap_and_edges(self.size,
                                                           self.subdiv,
                                                           self.minheight, self.layers,
                                                           oct=self.octaves,
                                                           repeatx=self.repeatx,
                                                           repeaty=self.repeaty,
                                                           base=self.base)
        self.dc.data['heightmap'] = (hm, qhm, edges)
        if not draw:
            return self.delta

        logging.info("Heightmap Generated, creating vertices")
        for x in range(len(hm)):
            for y in range(len(hm[0])):
                vert = self.dc.newVertex(np.array([x,y]) * self.subdiv)
                vert.data[VertE.RADIUS] = self.radius
                vert.data[VertE.STROKE] = np.array([qhm[x,y],0,0,1])
                if edges[x,y] == 1:
                    vert.data[VertE.STROKE][1] = 1
                self.delta.append(vert)

        return self.delta

    def unwind(self):
        self.dcel.purge(targets=self.delta)
        self.delta = []
