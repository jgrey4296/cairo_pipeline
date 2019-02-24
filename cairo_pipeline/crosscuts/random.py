import numpy as np
import cairo_utils as utils
import IPython
import logging as root_logger
from functools import partial
logging = root_logger.getLogger(__name__)

#call as a key, a shape, and a dict of params

#Layer to setup crosscuts
def setup(d, opts, data):
    """ Layer : random_setup
    Registers Crosscuts, in a namespace

    """
    seed = None
    if 'seed' in opts:
        seed = opts['seed']
    state = {'state' : np.random.RandomState(seed)}
    if 'start_state' in opts:
        state.update(opts['start_state'])
    if not d.has_crosscut('access',  namespace='random'):
        d.register_crosscuts({'access' : accessor,
                              'call' : call,
                              'reseed' : reseed },
                             namespace="random",
                             start_state=state)
    d.register_crosscuts(opts['pairs'], namespace="random" )
    #Setup the accessors
    return data

def accessor(d, args, state):
    """ Crosscut :  random accessor

    """
    #get the algorithm
    func = d._registered_crosscuts["random_{}".format(args['key'])]
    value = partial(func, state['state'], params=args['params'])
    return (value, state, args['data'])

def call(d, args, state):
    """ Crosscut :  call a registered random generator

    """
    #get the algorithm
    func, state, data = accessor(d, args, state)
    #call it
    values = func(args['shape'])
    return (values, state, data)

def reseed(d, args, state):
    r_state = d._crosscut_states['random']['state']
    r_state.seed(shape)
    return (value, state, args['data'])


#----------------------------------------
# Actual random functions
# Able to be used as crosscuts, or separately
#----------------------------------------
def uniform(state,shape=None, params=None):
    """ Get a shaped set of random floats in a range """
    default_params = { 'range' : [0,1] }
    default_params.update(params)
    if shape is None:
        shape = 1

    result = state.uniform(*default_params['range'], shape)
    return result

def additive(state, shape=None, params=None):
    """
    Create additive noise
    """
    if shape is None:
        shape = (1,)
    default_params = { 'base_freq' : 1,
                       'harmonics' : [1, 1.5,   2],
                       'amplitudes': [1, 0.8, 0.5],
                       'phases'    : [0,   0,   0],
                       'easing'    : ('linear', 0),
                       'offmul'    : [0, 1] }
    if args is not None:
        default_params.update(params)
    offset, mul = args['offmul']

    ts = np.linspace(0,utils.constants.TWOPI, shape[0])

    result = np.zeros((1, args['n']))
    for (h,a,p) in zip(args['harmonics'],args['amplitudes'],args['phases']):
        wave = np.sin(p + (ts * (base_freq * h))) * a
        result = np.row_stack((result, wave))
    combined = result.sum(axis=0)
    final = (offset + combined) * mul
    return final
