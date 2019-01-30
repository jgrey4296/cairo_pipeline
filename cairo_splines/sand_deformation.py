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
    ramp = easing(np.linspace(0,1,n), 0).reshape((n,1))
    ramp2 = easing_2(np.linspace(-1,1,n), 3.5).reshape((n,1))
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1,utils.constants.SAMPLE_DATA_LEN))

    for sample_set in samples:
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]

        # base random signal
        # TODO: make this a separate layer? make it FM or AM or additive?
        noise = easing(d.call('random', {'range': np.array([-1,1]) * opts['noise_mul'],
                                         'shape': (n,1) }), 0)
        speed = d.call('random', { 'range' : opts['speed'], 'shape' : (1, 1)})
        phase = d.call('random', { 'range' : opts['phase'], 'shape' : (1, 1)})
        scale = d.call('random', { 'range' : opts['scale'], 'shape' : (n, 1)})

        rads = (ramp2 * (speed * utils.umath.TWOPI)) + noise
        rads_reshaped = rads.reshape((n, 1))
        rotation = np.hstack((np.cos(phase + rads_reshaped),
                              np.sin(phase + rads_reshaped)))
        combined = rotation * scale
        i_xys = (xys + combined)
        recombined = np.column_stack((i_xys, rst))
        #recombine
        result = np.row_stack((result, recombined))

    d._samples = np.row_stack((np.zeros((1, utils.constants.SAMPLE_DATA_LEN)),
                               result[1:]))
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
        rads = d.call('random', { 'range': rad, 'shape': dis.shape })

        dirs_prime = dirs + rads
        rot_vector = np.array([np.cos(dirs_prime), np.sin(dirs_prime)]).T
        dist_scale = d.call('random', { 'range' : opts['mult'], 'shape': rot_vector.shape })
        scaled_rot = rot_vector * dist_scale

        grain_line = np.column_stack((xys[:-1], xys[:-1] + scaled_rot))

        result = np.row_stack((result, grain_line))

    d.add_lines(result)
    return data
