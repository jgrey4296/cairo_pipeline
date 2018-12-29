"""
Module that Implements a Hyphae like growth algorithm
"""
import numpy as np
from numpy.random import random
from math import pi, sin, cos
import pyqtree
import networkx as nx

import cairo_utils as utils
from cairo_utils.constants import PI, TWOPI, QUARTERPI
from simple_draw import SimpleDraw
#note to remember:
# spindex = pyqtree.Index(bbox=[0, 0, 100, 100])
# spindex.insert(item=item, bbox=item.bbox)
# matches = spindex.intersect(overlapbbox)

NEIGHBOURS = np.array([
    #[-1, -1], #top left
    [0, -1], #top
    #[1, -1], #top right
    [-1, 0], #left
    [1, 0], #right
    #[-1, 1, ], #bot left
    [0, 1], #bot
    #[1, 1]#bot right
])

# VARIABLES
BRANCH_AMNT = 0.1
DELTA = 1 / 100
HALF_DELTA = DELTA * 0.5
BAL_PI = PI - (PI * 0.5)
LINEPOINTS = 100
RADIUS = 0.002
NODE_NUM = 100
NODE_RECIPROCAL = 1 / NODE_NUM
NUM_START_POINTS = 5
__NEXT_NODE = 0

# Occupied locations grid:
grid = np.zeros((node_num, node_num), dtype=int)
# Paths graph
paths = nx.Graph()
# Nodes index
nodes = {}

def branch_pipeline(d, pipeline_data):

    return pipeline_data

def get_open_neighbours(, xy):
    """ Get the open neighbours of the specified point """
    unchecked_neighbours = xy + NEIGHBOURS
    in_bounds_min = (unchecked_neighbours >= 0).all(axis=1)
    in_bounds_max = (unchecked_neighbours <= .node_num).all(axis=1)
    valid_neighbours = unchecked_neighbours[(in_bounds_min * in_bounds_max)]
    open_neighbours = valid_neighbours[graph[valid_neighbours[:,0],
                                             valid_neighbours[:,1]] == 0]

    return open_neighbours
