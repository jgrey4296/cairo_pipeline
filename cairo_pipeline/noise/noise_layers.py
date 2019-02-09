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


def simple_noise(d, opts, data):
    """ Simple Displacement noise using additive sine signals  """
    n = data['n']
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1,utils.constants.SAMPLE_DATA_LEN))

    if 'test_displace_scale' in data:
        scales = data['test_displace_scale']
    else:
        scales = opts['scale']
    scale = 0
    if bool(scales):
        scale = scales.pop(0)
    data['test_displace_scale'] = scales

    envelope = utils.easings.lookup('pow_max_abs')(np.linspace(-1,1,n), 3.5).reshape((n,1))

    for i, sample_set in enumerate(samples):
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]
        base_freq, discard = d.call('random', { 'range': [2,3], 'shape': (1,1) })
        noise, discard = d.call('add_noise', {
            'base_freq'  : base_freq,
            'harmonics'  : [1, 1.5, 2, 4],
            'amplitudes' : [1, 0.5, 0.8, 0.6],
            'phases'     : np.zeros(4),
            'easing'     : ['sigmoid', 2],
            'offmul'     : [1, utils.constants.TWOPI],
            'n'          : n
        })
        rot =  envelope * np.column_stack((np.cos(noise), np.sin(noise))) * scale
        # rot = np.column_stack((np.zeros((n,1)), noise)) * 200
        transformed = xys + rot
        recombined = np.column_stack((transformed, rst))
        result = np.row_stack((result, recombined))

    d._samples = result
    return data

def __incorrect_noise_layer(d, opts, data):
    """ Treats data as sequences to be displaced by noisy sine signals """
    n = data['n']
    d_noise = np.zeros((1, n, 1))
    if 'displace_noise' in data:
        d_noise = data['displace_noise']

    easing_1 = utils.easings.lookup(opts['easing'][0][0])
    easing_2 = utils.easings.lookup(opts['easing'][1][0])
    ramp_1, discard = d.call('ease', { 'easing': easing_1,
                            'input': np.linspace(0,1,n),
                            'params' : opts['easing'][0] }).reshape((n,1))
    ramp_2, discard = d.call('ease', { 'easing' : easing_1,
                             'input'  : np.linspace(0,1,n),
                             'params' : opts['easing'][1]}).reshape((n,1))
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1,utils.constants.SAMPLE_DATA_LEN))

    for i,(sample_set,sd_noise) in enumerate(zip(samples, d_noise)):
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]

        # base random signal
        # TODO: make this a separate layer? make it FM or AM or additive?
        p_noise, discard = d.call('random', {'range': opts['p_noise'],  'shape': (n,1) })
        r_noise, discard = d.call('random', {'range' : opts['r_noise'], 'shape': (n,1) })
        speed, discard = d.call('random', { 'range' : opts['speed'], 'shape' : (1, 1)})
        phase, discard = d.call('random', { 'range' : opts['phase'], 'shape' : (1, 1)})
        scale, discard = d.call('random', { 'range' : opts['scale'], 'shape' : (n, 1)})

        rads = ramp_1 * ((speed * utils.umath.TWOPI) + r_noise)
        rotation = np.hstack((np.cos(phase + rads),
                              np.sin(phase + rads)))
        combined = (rotation * scale) + p_noise
        i_xys = xys + (ramp_2 * combined)
        # i_xys = utils.umath._interpolate(xys + (ramp_2 * combined), n)
        recombined = np.column_stack((i_xys, rst))
        #recombine
        d_noise[i] += p_noise
        result = np.row_stack((result, recombined))

    d._samples = result
    data['displace_noise'] = d_noise
    return data

def granulate_layer(d, opts, data):
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
