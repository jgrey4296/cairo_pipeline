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
    vals, data = d.call_crosscut('access',
                                 lookup={
                                     'dist_range' : [0,1],
                                     'n'    : 5,
                                     'override_dir' : False,
                                     'rad_range'  : [0, 3.142],
                                     'random' : ['uniform', {}],
                                 },
                                 opts=opts, data=data)
    dist_range, n, override_dir, rad_range, random_args= vals

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
        noise, data = d.call_crosscut('call',
                                      namespace='random',
                                      key=random_args[0],
                                      params=random_args[1],
                                      shape=dirs.shape,
                                      opts=opts, data=data)
        #TODO: Standardize scaling
        rads = rad_range[0] + (rad_range[1] * noise)
        dirs_prime = dirs + rads
        rot_vector = np.array([np.cos(dirs_prime), np.sin(dirs_prime)]).T
        noise, discard  = d.call_crosscut('call',
                                          namespace='random',
                                          key=random_args[0],
                                          params=random_args[1],
                                          shape=rot_vector.shape,
                                          opts=opts, data=data)
        rand_dist = dist_range[0] + (noise * dist_range[1])
        scaled_rot = rot_vector * rand_dist
        grain_line = np.column_stack((xys[:-1], xys[:-1] + scaled_rot))
        result = np.row_stack((result, grain_line))

    d.add_lines(result)
    return data
