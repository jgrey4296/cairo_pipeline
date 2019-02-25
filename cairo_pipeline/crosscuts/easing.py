import numpy as np
import cairo_utils as utils
import IPython
import logging as root_logger
from functools import partial
logging = root_logger.getLogger(__name__)

# call as a key, and a list of params

def call(d, args, state):
    """ Simplify calls to easings """
    easing, state = access(d, args, state)
    params = args['params']
    output = easing(args['input'], *params)

    return (output, state)

def access(d, args, state):
    """ Simple way to get an easing """
    key = args['key']
    easing = utils.easings.lookup(key)
    return (easing, state)
