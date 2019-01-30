"""
Defines a simple colour modifying pipeline layer
"""
import numpy as np
import cairo_utils as utils
from . import constants

def hue_rotate(d, opts, data):
    """ Create a gentle variation of colours """
    assert(data['c_type'] == 'hsla')
    n = data['n']
    easing = utils.easings.lookup(opts['easing'])
    samples = d._samples[1:].reshape((-1, n, utils.constants.SAMPLE_DATA_LEN))
    results = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))

    for sample_set in samples:
        non_colour = sample_set[:, :-utils.constants.COLOUR_SIZE]
        colours = sample_set[:, -utils.constants.COLOUR_SIZE:]

        noise = d.call('random', { 'range' : opts['noise'], 'shape': (n,1)})
        zeros = np.zeros((n,3))
        n_zzz = np.column_stack((noise, zeros))
        colours += n_zzz
        results = np.row_stack((results,
                                np.column_stack((non_colour, colours))))

    d._samples = results
    return data
