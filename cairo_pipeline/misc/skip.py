import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.constants import SAMPLE_DATA_LEN
from .. import constants
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def skip_layer(d, opts):
    """ Layer that skips over layers that come after it.
    Parameters: type (first, every), skip_num
    """
    current_step = d.data()['current_step']
    vals = d.call_crosscut('access',
                                 lookup={'count' : 5,
                                         'current_loop' : 0,
                                         'not' : False,
                                         'skip_num' : 1,
                                         'type' : 'first'},
                                 opts=opts)
    count, current_loop, invert, skip_num, skip_type = vals

    first = skip_type == 'first'
    every = skip_type == 'every'
    is_first = current_loop == 0
    is_count_loop = (current_loop % count) == 0

    if (first and not invert and is_first) \
       or (first and invert and not is_first) \
       or (every and not invert and is_count_loop) \
       or (every and invert and not is_count_loop):
        logging.info("Skipping {} layers".format(skip_num))
        d.set_data({'current_step' : current_step + skip_num })
