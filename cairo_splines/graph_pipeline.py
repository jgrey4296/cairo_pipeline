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

R = (1 / 42) * 0.5
NUM_POINTS_PER_LAYER = NUMPOINTS
NUM_LAYERS = NUM_LAYERS
ALPHA_STEP = 0.2

def graph_pipeline(d, pipeline_data):


    return pipeline_data