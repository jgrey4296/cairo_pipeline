import numpy as np
import cairo_utils as utils
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)


def no_op_call(d, args, state):
    """ A simple call that does nothing """

    return (None, state, args['data'])
