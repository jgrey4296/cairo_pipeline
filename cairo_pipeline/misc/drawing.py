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

def draw_layer(d, opts):
    """ Layer that draws the context so far to a file.
    Parameters: push, pixel (square, circle), draw
    """
    imgPath = d._imgPath
    vals = d.call_crosscut('access',
                                 lookup={
                                     'draw': True,
                                     'drawn' : 0,
                                     'imgName' :  'pipeline_test',
                                     'pixel' : 'circle',
                                     'push' : False,
                                     'subsample' : False,
                                 },
                                 opts=opts)
    draw, drawn, imgName, pixel, push, subsample = vals
    currentTime = time.gmtime()
    saveString = "{}{}_{}-{}_{}-{}".format(imgPath,
                                           imgName,
                                           currentTime.tm_min,
                                           currentTime.tm_hour,
                                           currentTime.tm_mday,
                                           currentTime.tm_mon,
                                           currentTime.tm_year)

    if push:
        d._ctx.save()

    if pixel == 'square':
        utils.drawing.draw_rect(d._ctx, d._samples)
    else:
        utils.drawing.draw_circle(d._ctx, d._samples)

    if subsample:
        if pixel == 'square':
            utils.drawing.draw_rect(d._ctx, subsample)
        else:
            utils.drawing.draw_circle(d._ctx, subsample)

    d.draw_text()
    if push:
        d._ctx.restore()

    if draw:
        logging.info("DRAWING {}: {}".format(drawn, saveString))
        utils.drawing.write_to_png(d._surface, saveString, i=drawn)
        no_val = d.call_crosscut('store',
                                       pairs={'drawn': drawn+1},
                                       target='data')

def clear_canvas_layer(d, opts):
    """ Layer that calls clear_canvas
    Parameters: clear_colour, clear_type, bbox
    """
    vals = d.call_crosscut('access',
                                 lookup={
                                     'bbox' : False,
                                     'clear_colour' : np.array([0,0,0,1]),
                                     'clear_type' : 'hsla',
                                 },
                                 opts=opts)
    bbox, clear_colour, clear_type = vals

    if clear_type == 'hsla':
        clear_colour = utils.colour.hsla2rgba(clear_colour.reshape((1,-1)))[0]

    utils.drawing.clear_canvas(d._ctx,
                               colour=clear_colour,
                               bbox=bbox)
