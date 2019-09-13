"""
Builds a heightmap
"""
import numpy as np
import cairo_utils as utils
from cairo_utils import heightmap
import logging as root_logger
logging = root_logger.getLogger(__name__)

def gen_heightmap(d, opts):
    vals = d.call_crosscut('access',
                                 lookup={
                                     'base'  : 1,
                                     'layers': 5 ,
                                     'min_height':  0,
                                     'octaves':  3,
                                     'repeat':  100,
                                     'size':  5
                                 },
                                 opts=opts)
    base, layers, min_height, octaves, repeat, size = vals

    hm, qhm, edges = heightmap.gen_heightmap_and_edges( size,
                                                        min_height,
                                                        layers,
                                                        oct=octaves,
                                                        repeatx=repeat[0],
                                                        repeaty=repeat[1],
                                                        base=base)

    d.call_crosscut('store', pairs={ 'heightmap' : hm,
                                     'quantized_heightmap' : qhm,
                                     'edge_heightmap' : edges },
                    target='data')
