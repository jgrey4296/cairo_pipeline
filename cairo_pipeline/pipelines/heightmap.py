"""
A simple pipeline that draws a heightmap
"""
import cairo_pipeline as cp
import cairo_utils as utils
import numpy as np
from . import crosscuts

simple = [ cp.misc.text.log_layer, {'message' : 'Heightmap pipeline'}
           , cp.misc.utils.set_var_layer, {'c_type' : 'hsla',
                                           'colour' : np.array([0, 0.5, 0.4, 0.1]),
                                           'drawn' : False}
           , *crosscuts.standard
           , cp.misc.drawing.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                                   'clear_type' : 'hsla' }
           , cp.noise.gen_heightmap , { 'size' : 20,
                                        'min_height' : 0,
                                        'layers' : 10,
                                        'octaves' : 4,
                                        'repeat' : [10, 10],
                                        'base' : 5 }
           #draw a grid of circles
           , cp.dcelp.geometry.create_circle_grid, { 'size' : 20,
                                                     'rad'  : [0.2*utils.constants.PI,
                                                               0.6*utils.constants.TWOPI],
                                                     'radius' : [50, 100] }
           #sample them
           , cp.misc.sampling.sample_layer, { 'n' : 500,
                                              'r' : 7,
                                              'c_type' : 'hsla',
                                              'target' : 'circle',
                                              'choice' : False,
                                              'random' : ['uniform', {}],
                                              'easing' : ['static', [1]]}
           #set lightness based on heightmap (using an operator to lookup from hm)
           , cp.colour.mapping.colour_lookup, { 'index' : 0 }
           , cp.colour.hsla_rgba_layer, {}
           # , cp.misc.utils.ipython_layer, {}
           , cp.misc.utils.set_var_layer, { 'draw' : True }
           , cp.misc.drawing.draw_layer, { 'pixel' : 'circle',
                                           'imgName' : 'heightmap_pipe_test',
                                           'push' : False,
                                           'subsample': False}

    ]
