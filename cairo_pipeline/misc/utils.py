""" Util Layer Pipeline
General Utility pipelines
"""
import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.constants import SAMPLE_DATA_LEN
from .. import constants
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def duplicate_layer(d, opts, data):
    """ Layer that duplicates the samples so far
    Parameters: num
    """
    samples = d._samples[1:,:]
    results = d._samples[:,:]
    for i in range(opts['num']):
        results = np.vstack((results, samples))
    d._samples = results
    return data

def wiggle_layer(d, opts, data):
    """ Layer that moves all samples slightly
    Parameters: dir, scale
    """
    xys = d._samples[:,:2]
    colours = d._samples[:,2:]

    dirs = opts['dir'][0] + (np.random.random((len(xys), 1)) * (opts['dir'][1] - opts['dir'][0]))
    rot = np.hstack((-np.cos(dirs), np.sin(dirs)))
    scale = opts['scale'] + (np.random.random((len(xys), 1)) * (opts['scale'][1] - opts['scale'][0]))
    xys += (scale * rot)

    d._samples = np.hstack((xys, colours))
    return data

def no_op_layer(d, opts, data):
    """ Layer that does nothing """
    return data

def fold_current(d, opts, data):
    """ Layer that takes the 'current' set of samples, and combines it into the main set """
    target = d._current[1:]
    d._samples = np.row_stack((d._samples, target))
    d._current = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))
    return data

def set_var_layer(d, opts, data):
    """ Layer that sets pipeline state variables """
    for x,y in opts.items():
        data[x] = y
    return data


