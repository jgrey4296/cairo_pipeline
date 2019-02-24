"""
Utilities to work with text
"""
import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.constants import SAMPLE_DATA_LEN
from .. import constants
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def text_layer(d, opts, data):
    """ Layer that registers text to be drawn.
    Parameters: colour, text
    """
    vals, data = d.call_crosscut('access',
                                 lookup={'colour': np.array([1,1,1,1]),
                                         'text' : 'Default Text'},
                                 opts=opts, data=data)
    colour, text= vals
    logging.info("text: {}".format(text))
    d.add_text(text.format(**data),
               [d._size[0]*0.1,
                d._size[1]*0.05],
               d._size[0]*0.02,
               colour)

    return data

def log_layer(d, opts, data):
    """ Layer that logs a formatted message, using variables bound in pipeline state """
    logging.info('----------')
    logging.info(opts['message'].format(**data))
    return data
