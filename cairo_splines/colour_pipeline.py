"""
Defines a simple colour modifying pipeline layer
"""
import numpy as np
import cairo_utils as utils
from . import constants

def ColourPipeline(d, opts, data):
    """ Create a gentle variation of colours """
    n = data['n']
    speed = opts['speed']
    easing = utils.easings.lookup(opts['easing'])

    samples = d._samples[1:].reshape((-1, n, constants.SAMPLE_DATA_LEN))
    ones = np.ones(n)
    c_i = (np.linspace(0, 1, n))
    rndMax = opts['rndsig'][1] - opts['rndsig'][0]
    results = np.zeros((1, 7))

    for sample_set in samples:
        non_colour = sample_set[:, :-constants.COLOUR_SIZE]
        colours = sample_set[:, -constants.COLOUR_SIZE:]


        rnd = easing(opts['rndsig'][0] + (np.random.random((n)) * rndMax) , 0)
        sig = ((c_i + rnd) * utils.constants.TWOPI) * opts['scale']
        cos_c = np.cos(sig)
        sin_c = np.sin(sig)
        inter_c = cos_c * sin_c

        combined = np.column_stack((cos_c, sin_c, inter_c, ones))

        col_prime = opts['base'] + (colours * combined)
        sig_col = easing(col_prime, 0, r=[0,1])
        col_prime2 = utils.easings.quantize(sig_col)

        target = col_prime
        if opts['target'] == 0:
            target = sig_col
        if opts['target'] == 1:
            target = col_prime2

        results = np.row_stack((results,
                                np.column_stack((non_colour, target))))

    if 'alpha' in opts:
        results[:,-1] = opts['alpha']
    if 'radius' in opts:
        results[:, -(constants.COLOUR_SIZE + 1)] = opts['radius']
    d._samples = results[1:]
    return data
