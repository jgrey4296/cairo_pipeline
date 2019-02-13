"""
Granulation noise
"""
import numpy as np
from numpy.random import random
from sklearn.preprocessing import normalize
import cairo_utils as utils
import IPython
from .. import constants
import IPython

import logging as root_logger
logging = root_logger.getLogger(__name__)


def granulate(d, opts, data):
    """ A Layer to granulate a signal of samples """
    n = data['n']
    rad = opts['rad']
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1, utils.constants.LINE_DATA_LEN))

    #Select a subset of points
    #sample from those, pull across the direction
    # and use them as the current point set
    # to be displaced in another layer

    for sample_set in samples:
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]
        ds = xys[:-1] - xys[1:]
        dirs = np.arctan2(ds[:,1], ds[:,0])
        rads, discard = d.call('random', { 'range': rad, 'shape': dirs.shape })

        dirs_prime = dirs + rads
        rot_vector = np.array([np.cos(dirs_prime), np.sin(dirs_prime)]).T
        dist_scale, discard  = d.call('random', { 'range' : opts['mult'],
                                                  'shape': rot_vector.shape })
        scaled_rot = rot_vector * dist_scale

        grain_line = np.column_stack((xys[:-1], xys[:-1] + scaled_rot))

        result = np.row_stack((result, grain_line))


    d.add_lines(result)
    return data
