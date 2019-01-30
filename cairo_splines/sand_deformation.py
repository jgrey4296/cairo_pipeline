"""
A Drawing class based on inconvergents sandsplines
"""
import numpy as np
from numpy.random import random
from sklearn.preprocessing import normalize
import cairo_utils as utils
import IPython
from .pdraw import PDraw
from . import constants
import IPython


def displace_layer(d, opts, data):
    """ Treats data as sequences to be displaced by noisy sine signals """
    n = data['n']
    easing = utils.easings.lookup(opts['easing'][0])
    easing_2 = utils.easings.lookup(opts['easing'][1])
    ramp = easing(np.linspace(-1,1,n), 0)
    ramp2 = easing_2(np.linspace(-1,1,n), 0.5)
    scale = opts['scale']
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1,utils.constants.SAMPLE_DATA_LEN))

    for sample_set in samples:
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]

        # base random signal
        # TODO: make this a separate layer? make it FM or AM or additive?
        noise = easing((1.0-2.0) * np.random.random(), 0) * opts['noise_mul']
        speed = opts['speed'][0] + (np.random.random() * (opts['speed'][1] - opts['speed'][0]))
        phase = opts['phase'][0] + (np.random.random() * (opts['phase'][1] - opts['phase'][0]))

        rads = ramp2 * (speed + noise) * utils.umath.TWOPI
        rads_reshaped = rads.reshape((n, 1))
        rotation = np.hstack((-np.cos(phase + rads_reshaped),
                              np.sin(phase + rads_reshaped)))
        combined = rotation * scale

        formatted = combined.T
        i_xys = (xys + combined).reshape((-1,2))
        recombined = np.column_stack((i_xys, rst))

        #recombine
        result = np.row_stack((result, recombined))

    d._samples = np.row_stack((np.zeros((1, utils.constants.SAMPLE_DATA_LEN),
                                        result)))
    return data

def granulate_layer(d, opts, data):
    n = data['n']
    rad = opts['rad']
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1, utils.constants.LINE_DATA_LEN))

    for sample_set in samples:
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]
        ds = xys[:-1] - xys[1:]
        dirs = np.arctan2(ds[:,1], ds[:,0])
        rads = rad[0] + (np.random.random(dirs.shape) * (rad[1] - rad[0]))

        dirs_prime = dirs + rads
        rot_vector = np.array([np.cos(dirs_prime), np.sin(dirs_prime)]).T
        dist_scale = opts['mult'][0] + \
            (np.random.random(rot_vector.shape) * (opts['mult'][1] - opts['mult'][0]))
        scaled_rot = rot_vector * dist_scale

        grain_line = np.column_stack((xys[:-1], xys[:-1] + scaled_rot))

        result = np.row_stack((result, grain_line))

    d.add_lines(result)
    return data
