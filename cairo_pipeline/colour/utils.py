"""
Basic utilites for colour
"""
import numpy as np
from cairo_utils.colour import rgba2hsla, hsla2rgba

import logging as root_logger
logging = root_logger.getLogger(__name__)


def hsla_rgba_layer(d, opts):
    """ Layer that converts hsla format colour samples, to rgba """
    vals = d.call_crosscut('access',
                                 lookup={ 'c_type' : 'hsla' } ,
                                 opts=opts)
    assert(vals[0] == 'hsla')
    samples = d._samples[:,:-4]
    colours = d._samples[:,-4:]

    rgba_ed = hsla2rgba(colours)
    d._samples = np.column_stack((samples, rgba_ed))
    d.call_crosscut('store', pairs={'c_type' : 'rgba' },
                    target='data')

def rgba_hsla_layer(d, opts):
    vals = d.call_crosscut('access',
                                 lookup={ 'c_type' : 'rbga' },
                                 opts=opts)
    assert(vals[0] == 'rgba')
    """ Layer that converts rgba format colour samples, to hsla """
    samples = d._samples[:,:-4]
    colours = d._samples[:,-4:]

    hsla_ed = rgba2hsla(colours)
    d._samples = np.column_stack((samples, hsla_ed))
    d.call_crosscut('store', pairs={'c_type' : 'hsla' },
                    target='data')
