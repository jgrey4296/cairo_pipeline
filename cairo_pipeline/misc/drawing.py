"""
Utilites to draw output
"""
import time
import numpy as np
from functools import partial
from itertools import islice
import cairo_utils as utils
from cairo_utils.constants import SAMPLE_DATA_LEN
from .. import constants
import IPython
import logging as root_logger
logging = root_logger.getLogger(__name__)

def draw_layer(d, opts, data):
    """ Layer that draws the context so far to a file.
    Parameters: push, pixel (square, circle), draw
    """
    imgPath = d._imgPath
    imgName = opts['imgName']
    currentTime = time.gmtime()
    saveString = "{}{}_{}-{}_{}-{}".format(imgPath,
                                           imgName,
                                           currentTime.tm_min,
                                           currentTime.tm_hour,
                                           currentTime.tm_mday,
                                           currentTime.tm_mon,
                                           currentTime.tm_year)
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

def clear_canvas_layer(d, opts, data):
    """ Layer that calls clear_canvas
    Parameters: clear_colour, clear_type, bbox
    """
    if 'clear_colour' not in data:
        data['clear_colour'] = opts['clear_colour']
        data['clear_type']   = opts['clear_type']
    clear_colour = data['clear_colour']
    clear_type   = data['clear_type']

    if 'bbox' not in opts:
        bbox = np.array([0,0, *d._size])
    else:
        bbox = opts['bbox']

    if clear_type == 'hsla':
        clear_colour = utils.colour.hsla2rgba(clear_colour.reshape((1,-1)))[0]

    utils.drawing.clear_canvas(d._ctx,
                               colour=clear_colour,
                               bbox=bbox)
    return data
