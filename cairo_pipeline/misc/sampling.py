""" Utilities to sample shapes """

import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.constants import SAMPLE_DATA_LEN
from .. import constants
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def sample_layer(d, opts, data):
    """ Layer that samples a specific set of geometry
    Parameters: n, r, colour, target, choice, easing
    """
    if 'n' not in opts and 'n' not in data:
        raise Exception('n is not specified in sampling')
    if 'n' not in data:
        data['n'] = opts['n']
    r = opts['r']
    colour = opts['colour']
    data['c_type'] = opts['c_type']
    target_data = d._geometry[opts['target']]
    target_sampler = constants.SAMPLER_LOOKUP[opts['target']]
    easing = None
    if 'easing' in opts:
        easing = opts['easing']
    if len(target_data) < 1:
        return data

    # from https://stackoverflow.com/questions/14262654/
    if opts['choice'] != -1:
        target_data = target_data[np.random.choice(target_data.shape[0],
                                                   size=int(len(target_data) * opts['choice'])),
                                                   :]

    new_samples = utils.umath.sample_wrapper(target_sampler,
                                             target_data[1:],
                                             data['n'],
                                             r,
                                             colour,
                                             easing=easing)

    d._samples = np.row_stack((d._samples, new_samples))
    d._sampled_geometry[opts['target']] = np.row_stack((d._sampled_geometry[opts['target']],
                                                        target_data))
    d._geometry[opts['target']] = np.zeros((1, target_data.shape[1]))
    return data

def subsample_layer(d, opts, data):
    n = opts['n']
    section_num = opts['sections'] + 1
    end_points = np.linspace(0,data['n'],section_num, dtype=int)
    segments = list(zip(end_points[:-1],end_points[1:]))
    subsample = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))
    samples = d._samples[1:].reshape((-1, data['n'], utils.constants.SAMPLE_DATA_LEN))
    for (i, sampleset) in enumerate(samples):
        xys = sampleset[:,:2]
        rst = sampleset[:,2:]
        for (start,end) in segments:
            rst_segment = rst[start:end].repeat(int(n/(end-start)), axis=0)
            i_xys = utils.umath._interpolate(xys[start:end], n)
            best_length = min(len(rst_segment), len(i_xys))
            combined = np.column_stack((i_xys[:best_length], rst_segment[:best_length]))
            subsample = np.row_stack((subsample, combined))

    data['subsample'] = subsample
    return data
