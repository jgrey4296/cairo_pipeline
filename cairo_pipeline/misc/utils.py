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
    vals, data = d.call_crosscut('access',
                                 lookup={'num': 1},
                                 opts=opts, data=data)
    num = vals[0]

    samples = d._samples[1:,:]
    results = d._samples[:,:]
    for i in range(num):
        results = np.vstack((results, samples))
    d._samples = results
    return data

def wiggle_layer(d, opts, data):
    """ Layer that moves all samples slightly
    Parameters: dir, scale
    """
    vals, data = d.call_crosscut('access',
                                 lookup={
                                     'dir' : [0, utils.constants.TWOPI],
                                     'random': ['uniform', {}],
                                     'scale': [1, 1],
                                 },
                                 opts=opts, data=data)
    dir_a, rand_params, scale_a = vals
    random, data = d.call_crosscut('access',
                                   namespace='random',
                                   key=rand_params[0],
                                   params=rand_params[1],
                                   opts=opts, data=data)

    xys = d._samples[:,:2]
    colours = d._samples[:,2:]

    dirs = dir_a[0] + (random((len(xys), 1)) * (dir_a[1] - dir_a[0]))
    rot = np.hstack((-np.cos(dirs), np.sin(dirs)))
    scale = scale_a + (random((len(xys), 1)) * (scale_a[1] - scale_a[0]))
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
    data.update(opts)
    return data

def ipython_layer(d, opts, data):
    IPython.embed(simple_prompt=True)
    return data
