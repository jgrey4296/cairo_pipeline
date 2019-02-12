import numpy as np
import cairo_utils as utils
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

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
