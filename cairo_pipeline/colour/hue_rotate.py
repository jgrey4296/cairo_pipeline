"""
Defines a simple colour modifying pipeline layer
"""
import numpy as np
import cairo_utils as utils
from .. import constants

def hue_rotate(d, opts, data):
    """ Create a gentle variation of colours """
    vals, data = d.call_crosscut('access',
                                 lookup={
                                     'easing' : ['linear', [0]],
                                     'n' : 5,
                                     'random' : ['uniform', {}]
                                 },
                                 opts=opts, data=data)
    easing_args, n, random_args= vals
    rotation, new_data = d.call_crosscut('pop',
                                         key='noise_range',
                                         opts=opts, data=data)


    rand_range=[rotation-(rotation*0.5),rotation]
    easing = d.call_crosscut('access',
                             key=easing_args[0],
                             params=easing_args[1],
                             namespace='easing',
                             opts=opts, data=data)
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    results = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))

    for sample_set in samples:
        non_colour = sample_set[:, :-utils.constants.COLOUR_SIZE]
        colours = sample_set[:, -utils.constants.COLOUR_SIZE:]

        noise, discard= d.call_crosscut('call',
                                        key=random_args[0],
                                        shape=(n,1),
                                        params=random_args[1],
                                        namespace='random',
                                        opts=opts, data=data)
        noise_scales = rand_range[1] + (rand_range[0] * noise)

        zeros = np.zeros((n,3))
        n_zzz = np.column_stack((noise, zeros))
        colours += n_zzz
        results = np.row_stack((results,
                                np.column_stack((non_colour, colours))))

    d._samples = results
    return new_data
