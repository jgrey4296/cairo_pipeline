"""
Builds a heightmap
"""
import numpy as np
import cairo_utils as utils
from cairo_utils import heightmap
import logging as root_logger
logging = root_logger.getLogger(__name__)

def gen_heightmap(d, opts, data):
    delta = []
    if not override and 'heightmap' in dc.data:
        return delta

    hm, qhm, edges = heightmap.gen_heightmap_and_edges(opts['size'],
                                                       opts['subdiv'],
                                                       opts['minheight'],
                                                       opts['layers'],
                                                       oct=opts['octaves'],
                                                       repeatx=opts['repeatx'],
                                                       repeaty=opts['repeaty'],
                                                       base=opts['base'])

    data['heightmap'] = (hm, qhm, edges)

    return delta
