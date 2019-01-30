""" Util Layer Pipeline
General Utility pipelines
"""
import numpy as np
from functools import partial
import cairo_utils as utils
from cairo_utils.colour import rgba2hsla, hsla2rgba
from cairo_utils.constants import SAMPLE_DATA_LEN
from . import constants
import IPython

import logging as root_logger
logging = root_logger.getLogger(__name__)


def make_repeat_layer(n, layers):
    """ Given a number of times to repeat,
    and a list of layers, create a layer to repeat those layers
    when called in PDraw.pipeline """
    assert(all([callable(x) for x in layers]))
    return partial(_repeat_layer, n, layers)

def _repeat_layer(n, layers, d, opts, data):
    """ The function used to create a repeat layer partial """
    for i in range(n):
        for l in layers:
            data = l(d, data)
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

def sample_layer(d, opts, data):
    """ Layer that samples a specific set of geometry
    Parameters: n, r, colour, target, choice, easing
    """
    if 'n' not in opts and 'n' not in data:
        raise Exception('n is not specified in sampling')
    if 'n' not in data:
        data['n'] = opts['n']
    r = opts['r']
    colour = opts['colour']
    target_data = d._geometry[opts['target']]
    target_sampler = constants.SAMPLER_LOOKUP[opts['target']]
    easing = None
    if 'easing' in opts:
        easing = opts['easing']
    if len(target_data) < 1:
        return data

    # from https://stackoverflow.com/questions/14262654/
    if opts['choice'] != -1:
        target_data = target_data[np.random.choice(target_data.shape[0],
                                                   size=int(len(target_data) * opts['choice'])),
                                                   :]

    new_samples = utils.umath.sample_wrapper(target_sampler,
                                             target_data[1:],
                                             data['n'],
                                             r,
                                             colour,
                                             easing=easing)

    d._samples = np.row_stack((d._samples, new_samples))
    d._sampled_geometry[opts['target']] = np.row_stack((d._sampled_geometry[opts['target']],
                                                        target_data))
    d._geometry[opts['target']] = np.zeros((1, target_data.shape[1]))
    return data


def draw_layer(d, opts, data):
    """ Layer that draws the context so far to a file.
    Parameters: push, pixel (square, circle), draw
    """
    saveString = opts['saveString']
    drawn = 0
    if 'drawn' in data:
        drawn = data['drawn']

    if 'push' in opts:
        d._ctx.save()

    if opts['pixel'] == 'square':
        utils.drawing.draw_rect(d._ctx, d._samples)
    else:
        utils.drawing.draw_circle(d._ctx, d._samples)

    d.draw_text()
    if 'push' in opts:
        d._ctx.restore()

    if 'draw' in opts:
        utils.drawing.write_to_png(d._surface, saveString, i=drawn)
        data['drawn'] = drawn + 1
    return data

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

def duplicate_layer(d, opts, data):
    """ Layer that duplicates the samples so far
    Parameters: num
    """
    samples = d._samples[1:,:]
    results = d._samples[:,:]
    for i in range(opts['num']):
        results = np.vstack((results, samples))
    d._samples = results
    return data

def wiggle_layer(d, opts, data):
    """ Layer that moves all samples slightly
    Parameters: dir, scale
    """
    xys = d._samples[:,:2]
    colours = d._samples[:,2:]

    dirs = opts['dir'][0] + (np.random.random((len(xys), 1)) * (opts['dir'][1] - opts['dir'][0]))
    rot = np.hstack((-np.cos(dirs), np.sin(dirs)))
    scale = opts['scale'] + (np.random.random((len(xys), 1)) * (opts['scale'][1] - opts['scale'][0]))
    xys += (scale * rot)

    d._samples = np.hstack((xys, colours))
    return data

def hsla_rgba_layer(d, opts, data):
    """ Layer that converts hsla format colour samples, to rgba """
    samples = d._samples[:,:-4]
    colours = d._samples[:,-4:]

    rgba_ed = hsla2rgba(colours)
    d._samples = np.column_stack((samples, rgba_ed))
    return data

def rgba_hsla_layer(d, opts, data):
    """ Layer that converts rgba format colour samples, to hsla """
    samples = d._samples[:,:-4]
    colours = d._samples[:,-4:]

    hsla_ed = rgba2hsla(colours)

    d._samples = np.column_stack((samples, hsla_ed))
    return data

def no_op_layer(d, opts, data):
    """ Layer that does nothing """
    return data

def fold_current(d, opts, data):
    """ Layer that takes the 'current' set of samples, and combines it into the main set """
    target = d._current[1:]
    d._samples = np.row_stack((d._samples, target))
    d._current = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))
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

def skip_layer(d, opts, data):
    """ Layer that skips over layers that come after it.
    Parameters: type (first_only, every, not_first), skip_num
    """
    first_only = opts['type'] == 'first_only' and data['loop_num'] == 0
    repeatable = opts['type'] == 'every' and \
        data['current_loop'] % opts['every'] == 0
    not_first = opts['type'] == 'not_first' and data['loop_num'] > 0
    skip_num = 1
    if 'num' in opts:
        skip_num = opts['skip_num']
    if first_only or repeatable or not_first:
        data['current_step'] += skip_num
    return data

def clear_loop_layer(d, opts, data):
    """ Layer that resets the loop count """
    data['current_loop'] = 0
    return data

def finish_layer(d, opts, data):
    """ Layer that forces the pipeline to stop """
    data['finish'] = True
    return data

def log_layer(d, opts, data):
    """ Layer that logs a formatted message, using variables bound in pipeline state """
    logging.info('----------')
    logging.info(data['message'].format(**data))
    return data

def clear_canvas_layer(d, opts, data):
    """ Layer that calls clear_canvas
    Parameters: clear_colour, clear_type, bbox
    """
    if 'clear_colour' not in data:
        data['clear_colour'] = opts['clear_colour']
        data['clear_type']   = opts['clear_type']
    clear_colour = data['clear_colour']
    clear_type   = data['clear_type']

    if clear_type == 'hsla':
        clear_colour = utils.colour.hsla2rgba(clear_colour)

    utils.drawing.clear_canvas(d._ctx,
                               colour=clear_colour,
                               bbox=opts['bbox'])
    return data

def set_var_layer(d, opts, data):
    """ Layer that sets pipeline state variables """
    for x,y in opts.items():
        data[x] = y
