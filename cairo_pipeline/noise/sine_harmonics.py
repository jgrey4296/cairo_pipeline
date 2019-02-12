"""
Additive Singe based noise
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


def sine_harmonic_noise(d, opts, data):
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

