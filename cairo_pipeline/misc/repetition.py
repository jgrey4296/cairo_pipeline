"""
Utilities to create repetition layers
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

def make_repeat_layer(layers):
    """ Given a number of times to repeat,
    and a list of layers, create a layer to repeat those layers
    when called in PDraw.pipeline """
    return partial(_repeat_layer, layers)

def _repeat_layer(layers, d, opts, data):
    """ The function used to create a repeat layer partial """
    pipe_pairs = list(zip(islice(layers, 0, len(layers), 2),
                          islice(layers, 1, len(layers), 2)))
    pipeline_length = len(pipe_pairs)
    the_data = data
    for i in range(opts['num']):
        for l,o in pipe_pairs:
            logging.info("Looping Layer: {}".format(l.__name__))
            the_data = l(d, o, the_data)
    logging.info("Looping Finished")
    return data


def make_repeat_transform_layer(layers):
    """ Given a number of times to repeat,
    and a list of layers, create a layer to repeat those layers
    when called in PDraw.pipeline """
    return partial(_repeat_transform_layer, layers)

def _repeat_transform_layer(layers, d, opts, data):
    """ The function used to create a repeat layer partial """
    pipe_pairs = list(zip(islice(layers, 0, len(layers), 2),
                          islice(layers, 1, len(layers), 2)))
    pipeline_length = len(pipe_pairs)
    the_data = data
    transform = opts['transform']
    for i in range(opts['num']):
        for l,o in pipe_pairs:
            o_t = transform(i,o,data)
            logging.info("Looping Layer: {}".format(l.__name__))
            the_data = l(d, o_t, the_data)
    logging.info("Looping Finished")
    return data


def make_conditional_repeat_layer(cond, layers):
    """ Given a condition, and a list of layers,
    create a layer that when called repeats the layers until
    the condition is true on the pipeline_data """
    assert(all([callable(x) for x in layers]))
    assert(callable(x))
    return partial(_conditional_repeat_layer, cond, layers)

def _conditional_repeat_layer(cond, layers, d, opts, data):
    """ The function used to create a conditional repeat layer partial """
    i = constants.MAX_LAYER_LOOP
    while not cond(data) and i > 0:
        for l in layers:
            data = l(d, data)
        i -= 1
    return data

def loop_start_layer(d, opts, data):
    """ Layer that sets where a loop returns to """
    data['return_to_step'] = data['current_step']
    return data

def loop_layer(d, opts, data):
    """ Layer that triggers a loop
    Parameters: max_loops
    """
    if 'max_loops' in opts:
        data['max_loops'] = opts['max_loops']
    if data['current_loop'] < data['max_loops']:
        data['current_step'] = data['return_to_step'] - 1
        data['current_loop'] += 1
    return data

def clear_loop_layer(d, opts, data):
    """ Layer that resets the loop count """
    data['current_loop'] = 0
    return data

def finish_layer(d, opts, data):
    """ Layer that forces the pipeline to stop """
    data['finish'] = True
    return data
