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
    colour = [1,1,1,1]
    if 'colour' in opts:
        colour = opts['colour']

    d.add_text(opts['text'],
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
