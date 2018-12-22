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
    """ Draws layers of points """

    def __init__(self, ctx, size_tuple, numPoints=8, num_layers=1):
        super().__init__(self, ctx, size_tuple)
        self.r = (1 / 42) * 0.5
        self.num_points_per_layer = numPoints
        self.num_layers = num_layers
        self.alpha_step = 0.2

    def generate(self, locations=None):
        if locations is None:

        #create a set of nodes
        ps = utils.math.sampleCircle(0.5, 0.5, 0.4, self.num_points_per_layer)


    def iterate(self, i, frontier=None):

        return []

    def draw(self):
            #Create a hull around the points
            # hull = ConvexHull(ps)

            # #Draw edges of the convex hull
            # last = None
            # for j, index in enumerate(hull.vertices):
            #     x,y = ps[index]
            #     logging.info("Drawing point: {}: ( {} {} )".format(j, x, y))
            #     utils.drawing.draw_circle(self._ctx, x, y, self.r)
            #     if last is not None:
            #         self._ctx.move_to(*ps[last])
            #         self._ctx.line_to(x,y)
            #         self._ctx.stroke()
            #     last = index

            # self._ctx.move_to(*ps[last])
            # self._ctx.line_to(*(ps[hull.vertices[0]]))
            # self._ctx.stroke()
