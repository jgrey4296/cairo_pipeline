"""
A simple pipeline that draws a heightmap
"""
import cairo_pipeline as cp
import cairo_utils as utils
import numpy as np
from . import crosscuts

simple = [ cp.misc.text.log_layer, {'message' : 'Noisy Circle pipeline'}
           , *crosscuts.standard
           , cp.misc.utils.set_var_layer, {'c_type' : 'hsla',
                                           'colour' : np.array([0, 0.5, 0.4, 0.5]),
                                           'drawn' : False}
           , cp.misc.drawing.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                                   'clear_type' : 'hsla' }
           , cp.noise.gen_heightmap , { 'size' : 20,
                                        'min_height' : 0,
                                        'layers' : 10,
                                        'octaves' : 4,
                                        'repeat' : [10, 10],
                                        'base' : 5 }
           , cp.dcelp.geometry_layers.create_line, {}
           #sample them
           , cp.misc.sampling.sample_layer, { 'n' : 1000,
                                              'r' : 5,
                                              'c_type' : 'hsla',
                                              'target' : 'line',
                                              'choice' : False,
                                              'random' : ['uniform', {}],
                                              'easing' : ['static', [1]]}
           #set lightness based on heightmap (using an operator to lookup from hm)
           , cp.noise.sine_harmonic_noise, { 'scale' : 100,
                                             'random' : ['additive', { 'base_freq' : 5,
                                                                       'harmonics' : [1]}]}
           , cp.colour.mapping.colour_lookup, { 'index' : 0 }
           , cp.colour.hsla_rgba_layer, {}
           # , cp.misc.utils.ipython_layer, {}
           , cp.misc.utils.set_var_layer, { 'draw' : True }
           , cp.misc.drawing.draw_layer, { 'pixel' : 'circle',
                                           'imgName' : 'noisy_circle',
                                           'push' : False,
                                           'subsample': False}

    ]
