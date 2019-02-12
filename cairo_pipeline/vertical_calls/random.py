import numpy as np
import cairo_utils as utils
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def simple_random_call(d, args, state, data):
    """ Get a shaped set of random floats in a range """
    if not isinstance(args['range'], list):
        result = np.ones(args['shape']) * args['range']
        state['last'] = result
        return (result, state, data)

    low, high = args['range']
    shape = args['shape']
    result= low + (np.random.random(shape) * (high - low))
    state['last'] = result
    return (result, state, data)

def additive_noise(d, args, state, data):
    """
    Create additive noise
    """
    base_freq = args['base_freq']
    harmonics = args['harmonics']
    amplitudes = args['amplitudes']
    phases = args['phases']
    easing = utils.easings.lookup(args['easing'][0])
    offset, mul = args['offmul']

    ts = np.linspace(0,utils.constants.TWOPI, args['n'])

    result = np.zeros((1, args['n']))
    for (h,a,p) in zip(harmonics,amplitudes,phases):
        wave = np.sin(p + (ts * (base_freq * h))) * a
        result = np.row_stack((result, wave))
    combined = result.sum(axis=0)
    shaped = d.call('ease', { 'easing' : easing,
                              'input'  : combined,
                              'params' : args['easing']})[0].reshape((args['n'],1))
    final = (offset + shaped) * mul
    return (final, state, data)
