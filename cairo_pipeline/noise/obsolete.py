"""
A Failed attempt
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
