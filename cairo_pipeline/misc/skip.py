import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.constants import SAMPLE_DATA_LEN
from .. import constants
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def skip_layer(d, opts, data):
    """ Layer that skips over layers that come after it.
    Parameters: type (first, every), skip_num
    """

    first = opts['type'] == 'first'
    is_first = data['current_loop'] == 0
    every = opts['type'] == 'every'
    count = 5
    if 'count' in opts:
        count = opts['count']
    is_count_loop = (data['current_loop'] % count) == 0
    invert = 'not' in opts and opts['not']
    skip_num = 1
    if 'num' in opts:
        skip_num = opts['skip_num']

    if (first and not invert and is_first) \
       or (first and invert and not is_first) \
       or (every and not invert and is_count_loop) \
       or (every and invert and not is_count_loop):
        logging.info("Skipping {} layers".format(skip_num))
        data['current_step'] += skip_num
    return data
