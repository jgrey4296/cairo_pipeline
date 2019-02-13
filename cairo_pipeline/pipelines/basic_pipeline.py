"""
A Simple pipeline to sample and granulate
"""
import cairo_pipeline as cp
import cairo_utils as utils
import numpy as np

simple = [
    cp.misc.utils.no_op_layer, {}
    , cp.calls.register_calls, { 'random': cp.calls.random.simple_random_call,
                                    'ease' : cp.calls.easing.run_easing,
                                    'add_noise' : cp.calls.random.additive_noise,
                                    'pop' : cp.calls.value_control.pop_value }
    # , cp.dcelp.geometry.create_two_splines, {}
    # , cp.dcelp.geometry.create_points, {}
    # , cp.dcelp.geometry.create_line, {}
    # , cp.dcelp.geometry.create_lines, { 'num' : 15 }
    # , cp.dcelp.geometry.create_grid, { 'num': 10 }
    , cp.dcelp.geometry.create_circle, {}
    , cp.misc.text.text_layer, { 'text' : 'basic_pipeline' }
    , cp.misc.sampling.sample_layer, { 'n' : 3000,
                                       'r' : 3,
                                       'colour' : np.array([300, 0.4, 0.4, 0.15]),
                                       'c_type' : 'hsla',
                                       'target' : 'circle',
                                       'choice' : -1}
    #--------------------
    , cp.misc.repetition.loop_start_layer, {}
    , cp.misc.text.log_layer, { 'message' : 'Loop: {current_loop}' }

    , cp.misc.skip.skip_layer, { 'type' : 'first' }
    , cp.colour.rgba_hsla_layer, {}

    # , cp.noise.simple_harmonic_noise, {'scale': [280, 10, 50, -20, 50, 20, -10] }
    , cp.misc.skip.skip_layer, { 'type' : 'first', 'not' : True, 'skip_num': 2}
    , cp.noise.granulate, {'rad' : [-utils.constants.QUARTERPI,
                                    -utils.constants.QUARTERPI+0.4],
                           'mult'  : [200,200],
                           'choice': 0.4}
    # , cp.misc.sampling.sample_layer, { 'n' : 500,
    #                                    'r' : 3,
    #                                    'colour' : np.array([300, 0.4, 0.4, 0.15]),
    #                                    'c_type' : 'hsla',
    #                                    'target' : 'line',
    #                                    'choice' : 0.05}

    # , cp.misc.skip.skip_layer, { 'type' : 'first', 'not' : True, 'skip_num': 1}
    # , cp.misc.utils.duplicate_layer,  { 'num' : 3}
    , cp.misc.utils.wiggle_layer, { 'scale' : [0,2],
                         'dir' : [0, utils.constants.TWOPI]}

    , cp.colour.hue_rotate, {'easing': 'sigmoid',
                             'noise_range' : [30,30,-40,-40,25] }

    , cp.colour.hsla_rgba_layer, {}
    , cp.misc.drawing.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                            'clear_type' : 'hsla' }

    , cp.misc.skip.skip_layer, { 'type' : 'every',
                                 'count': 1,
                                 'not' : True}
    , cp.misc.utils.set_var_layer, { 'draw': True }

    # , cp.misc.sampling.subsample_layer, { 'n': 1000,
    #                         'sections': 20 }
    , cp.misc.drawing.draw_layer, { 'pixel' : 'circle',
                                    'imgName' : 'basic_pipeline',
                                    'draw'  : True}

    , cp.misc.utils.set_var_layer, { 'clear_colour' : np.array([0,0,0,0]),
                                     'draw' : False}
    , cp.misc.repetition.loop_layer, { 'max_loops' : 7}
    #--------------------
    , cp.misc.repetition.finish_layer, {}
]
