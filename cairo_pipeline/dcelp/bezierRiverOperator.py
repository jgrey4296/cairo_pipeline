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

def select_river_sides(d, opts, data):

    return data


def claim_river_space(d, opts, data):

    return data

def fill_lowland(d, opts, data):

    return data
