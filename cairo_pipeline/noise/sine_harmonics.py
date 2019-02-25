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


def sine_harmonic_noise(d, opts):
    """ Simple Displacement noise using additive sine signals  """
    vals = d.call_crosscut('access',
                                 lookup={
                                     'easing' : ['static', 1],
                                     'n' : 1,
                                     'random' : ['additive', None],
                                     'scale' : 1,
                                 },
                                 opts=opts)
    envelope_args, n, rand_args, scale = vals
    envelope = d.call_crosscut('access',
                               namespace='easing',
                               key=envelope_args[0],
                               opts=opts)

    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    result = np.zeros((1,utils.constants.SAMPLE_DATA_LEN))

    env = envelope(np.linspace(0,1,n))

    for i, sample_set in enumerate(samples):
        xys = sample_set[:,:2]
        rst = sample_set[:,2:]
        noise = d.call_crosscut( rand_args[0],
                                          namespace='random',
                                          args=rand_args[1],
                                          shape=xys.shape,
                                          opts=opts)
        rot = env * np.column_stack((np.cos(noise), np.sin(noise))) * scale
        transformed = xys + rot
        recombined = np.column_stack((transformed, rst))
        result = np.row_stack((result, recombined))

    d._samples = result
