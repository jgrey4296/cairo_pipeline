"""
Defines a simple colour modifying pipeline layer
"""
import numpy as np
import cairo_utils as utils
from .. import constants
import logging as root_logger
import IPython
logging = root_logger.getLogger(__name__)

def hue_rotate(d, opts):
    """ Create a gentle variation of colours """
    vals = d.call_crosscut('access',
                           lookup={
                               'easing' : ['linear', [0]],
                               'n' : 5,
                               'random' : ['uniform', {}],
                           },
                           opts=opts)
    easing_args, n, random_args= vals
    rotation_min = d.call_crosscut('cycle',
                                   key='noise_range_min',
                                   opts=opts)
    rotation_max = d.call_crosscut('cycle',
                                   key='noise_range_max',
                                   opts=opts)

    rand_range=[rotation_min, rotation_max]
    easing = d.call_crosscut('access',
                             key=easing_args[0],
                             params=easing_args[1],
                             namespace='easing',
                             opts=opts)
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    results = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))

    for sample_set in samples:
        non_colour = sample_set[:, :-utils.constants.COLOUR_SIZE]
        colours = sample_set[:, -utils.constants.COLOUR_SIZE:]

        noise = d.call_crosscut('call',
                                key=random_args[0],
                                shape=(n,1),
                                params=random_args[1],
                                namespace='random',
                                opts=opts)
        eased_noise = easing(noise, *easing_args[1])
        noise_scaled = utils.umath.scale(eased_noise, rand_range)

        zeros = np.zeros((n,3))
        n_zzz = np.column_stack((noise_scaled, zeros))
        colours += n_zzz
        results = np.row_stack((results,
                                np.column_stack((non_colour, colours))))

    d._samples = results
