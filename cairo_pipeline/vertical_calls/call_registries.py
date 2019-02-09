"""
A Module of modular calls that can be made from layers through
the pdraw object
"""
import numpy as np
import cairo_utils as utils
import IPython

def no_op_call(d, args, state, data):
    """ A simple call that does nothing """
    return (None, state, data)

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

def run_easing(d, args, state, data):
    """ Simplify calls to easings """
    easing = args['easing']
    params = args['params']
    if len(params) == 4:
        return (easing(args['input'], params[1], params[2], params[3]),
                state)
    elif len(params) == 3:
        return (easing(args['input'], params[1], codomain_e=params[2]),
                state)
    else:
        return (easing(args['input'], params[1]),
                state, data)

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

def pop_value(d, args, state, data):
    if args['var'] in data:
        the_list = data[args['var']]
    else:
        the_list = args['opts'][args['var']]
    if len(the_list) > 1:
        value = the_list.pop(0)
    else:
        value = the_list[0]
    data[args['var']] = the_list
    return (value, state, data)
