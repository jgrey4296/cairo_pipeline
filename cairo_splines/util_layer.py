""" Util Layer Pipeline
General Utility pipelines
"""
import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.colour import rgba2hsla, hsla2rgba
from cairo_utils.constants import SAMPLE_DATA_LEN
from . import constants
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
    data['c_type'] = opts['c_type']
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
    draw = data['draw']
    drawn = 0
    if 'drawn' in data:
        drawn = data['drawn']

    if 'push' in opts:
        d._ctx.save()

    if opts['pixel'] == 'square':
        utils.drawing.draw_rect(d._ctx, d._samples)
    else:
        utils.drawing.draw_circle(d._ctx, d._samples)

    if 'subsample' in data:
        if opts['pixel'] == 'square':
            utils.drawing.draw_rect(d._ctx, data['subsample'])
        else:
            utils.drawing.draw_circle(d._ctx, data['subsample'])

    d.draw_text()
    if 'push' in opts:
        d._ctx.restore()

    if draw:
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
    assert(data['c_type'] == 'hsla')
    samples = d._samples[:,:-4]
    colours = d._samples[:,-4:]

    rgba_ed = hsla2rgba(colours)
    d._samples = np.column_stack((samples, rgba_ed))
    data['c_type'] = 'rgba'
    return data

def rgba_hsla_layer(d, opts, data):
    assert(data['c_type'] == 'rgba')
    """ Layer that converts rgba format colour samples, to hsla """
    samples = d._samples[:,:-4]
    colours = d._samples[:,-4:]

    hsla_ed = rgba2hsla(colours)
    d._samples = np.column_stack((samples, hsla_ed))
    data['c_type'] = 'hsla'
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
    logging.info(opts['message'].format(**data))
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
        clear_colour = utils.colour.hsla2rgba(clear_colour.reshape((1,-1)))[0]

    utils.drawing.clear_canvas(d._ctx,
                               colour=clear_colour,
                               bbox=opts['bbox'])
    return data

def set_var_layer(d, opts, data):
    """ Layer that sets pipeline state variables """
    for x,y in opts.items():
        data[x] = y
    return data


def subsample_layer(d, opts, data):
    n = opts['n']
    section_num = opts['sections'] + 1
    end_points = np.linspace(0,data['n'],section_num, dtype=int)
    segments = list(zip(end_points[:-1],end_points[1:]))
    subsample = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))
    samples = d._samples[1:].reshape((-1, data['n'], utils.constants.SAMPLE_DATA_LEN))
    for (i, sampleset) in enumerate(samples):
        xys = sampleset[:,:2]
        rst = sampleset[:,2:]
        for (start,end) in segments:
            rst_segment = rst[start:end].repeat(int(n/(end-start)), axis=0)
            i_xys = utils.umath._interpolate(xys[start:end], n)
            best_length = min(len(rst_segment), len(i_xys))
            combined = np.column_stack((i_xys[:best_length], rst_segment[:best_length]))
            subsample = np.row_stack((subsample, combined))

    data['subsample'] = subsample
    return data

