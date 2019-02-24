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
    vals, data = d.call_crosscut('access',
                        lookup={
                            'c_type': 'hsla',
                            'choice': False,
                            'colour': np.array([0,0,1,1]),
                            'easing': ['static',1],
                            'n': 5,
                            'r': 3,
                            'random': ['uniform', {}],
                            'target': 'circle',
                        },
                        opts=opts , data=data)
    c_type, choice, colour, easing, n, r, random_params, target = vals
    random, data = d.call_crosscut('access',
                                   namespace='random',
                                   key=random_params[0],
                                   params=random_params[1],
                                   opts=opts, data=data)
    #TODO: Change this to crosscuts
    target_data = d._geometry[target]
    target_sampler = constants.SAMPLER_LOOKUP[target]

    if len(target_data) < 1:
        return data

    if choice:
        target_data = target_data[choice(target_data.shape[0]), :]

    new_samples = utils.umath.sample_wrapper(target_sampler,
                                             target_data[1:],
                                             n,
                                             r,
                                             colour,
                                             easing=easing,
                                             random=random)

    d._samples = np.row_stack((d._samples, new_samples))
    d._sampled_geometry[target] = np.row_stack((d._sampled_geometry[target],
                                                        target_data))
    d._geometry[target] = np.zeros((1, target_data.shape[1]))

    d.call_crosscut('store', pairs={'n': n,
                                    'c_type' : c_type },
                    target='data', data=data)

    return data

def subsample_layer(d, opts, data):
    vals, data = d.call_crosscut('access',
                                 lookup={'n': 5,
                                         'sections': 1},
                                 opts=opts,
                                 data=data)
    n, sections = vals
    sections += 1

    end_points = np.linspace(0, n, section_num, dtype=int)
    segments = list(zip(end_points[:-1],end_points[1:]))
    subsample = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
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
