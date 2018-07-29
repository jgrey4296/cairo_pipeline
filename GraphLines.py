"""
A Class to Draw layers of points on a circle, connected by lines 
"""
import cairo_utils as utils
import numpy as np
from SimpleDraw import SimpleDraw
from functools import cmp_to_key
from scipy.spatial import ConvexHull
import IPython

import logging as root_logger
logging = root_logger.getLogger(__name__)


class GraphLines(SimpleDraw):
    """ The barest abstract class for drawing  """

    def __init__(self, ctx, sizeTuple, numPoints=8, numLayers=1):
        super().__init__(ctx, sizeTuple)
        self.r = (1 / 42) * 0.5
        self.numPointsPerLayer = numPoints
        self.numLayers = numLayers
        self.alphaStep = 0.2

    def draw(self):
        """ Abstract Method that is called to draw to the canvas """
        utils.drawing.clear_canvas(self._ctx)
        self._ctx.set_line_width(0.01)
        alpha = 0
        for i in range(self.numLayers):
            alpha = utils.math.clamp(alpha + self.alphaStep, 0, 1)

            self._ctx.set_source_rgba(*np.random.random(3), alpha)
            ps = utils.math.sampleCircle(0.5, 0.5, 0.4, self.numPointsPerLayer)
            #ps = np.random.random((self.numPointsPerLayer, 2))
            assert(len(ps) == self.numPointsPerLayer)
            hull = ConvexHull(ps)

            last = None
            for j, index in enumerate(hull.vertices):
                x,y = ps[index]
                logging.info("Drawing point: {}: ( {} {} )".format(j, x, y))
                utils.drawing.drawCircle(self._ctx, x, y, self.r)
                if last is not None:
                    self._ctx.move_to(*ps[last])
                    self._ctx.line_to(x,y)
                    self._ctx.stroke()
                last = index

            self._ctx.move_to(*ps[last])
            self._ctx.line_to(*(ps[hull.vertices[0]]))
            self._ctx.stroke()

            for x,y in ps:
                utils.drawing.drawCircle(self._ctx, x, y, self.r)
