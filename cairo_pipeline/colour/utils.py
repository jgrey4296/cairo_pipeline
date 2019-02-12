"""
Basic utilites for colour
"""
import numpy as np
from cairo_utils.colour import rgba2hsla, hsla2rgba

import logging as root_logger
logging = root_logger.getLogger(__name__)


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
