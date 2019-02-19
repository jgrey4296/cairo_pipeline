"""
A simple pipeline that draws a heightmap
"""
import cairo_pipeline as cp
import cairo_utils as utils
import numpy as np

heightmap_p = [ cp.misc.utils.no_op_layer, {}
                , cp.misc.drawing.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                                        'clear_type' : 'hsla' }
                , cp.noise.gen_heightmap , { 'size' : 20,
                                             'minheight' : 0,
                                             'layers' : 10,
                                             'octaves' : 3,
                                             'repeatx' : 10,
                                             'repeaty' : 10,
                                             'base' : 0 }
                #draw a grid of circles
                , cp.dcelp.geometry.create_circle_grid, { 'size' : 10,
                                                          'rad'  : [0, utils.constants.TWOPI],
                                                          'radius' : [0, 200] }
                #sample them
                , cp.misc.sampling.sample_layer, { 'n' : 3000,
                                                   'r' : 3,
                                                   'colour' : np.array([300, 0.4, 0.4, 0.15]),
                                                   'c_type' : 'hsla',
                                                   'target' : 'circle',
                                                   'choice' : -1 }
                #set lightness based on heightmap (using an operator to lookup from hm)

                , cp.colour.hsla_rgba_layer, {}
                , cp.misc.utils.set_var_layer, { 'draw' : True } 
                , cp.misc.drawing.draw_layer, { 'pixel' : 'circle',
                                                'imgName' : 'heightmap_pipe_test',
                                                'draw' : True}
    ]
