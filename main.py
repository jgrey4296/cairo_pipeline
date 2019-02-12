#!/Users/jgrey/anaconda/bin/python
import cairo
import logging
import math
import numpy as np
import sys
import time
import cairo_utils as utils
import cairo_pipeline as cp

#constants
N = 12
imgPath = "./imgs/"
imgName = "initialTest"
currentTime = time.gmtime()
FONT_SIZE = 0.03
FULL = utils.easings.CODOMAIN.FULL
LEFT = utils.easings.CODOMAIN.LEFT
RIGHT = utils.easings.CODOMAIN.RIGHT

#format the name of the image to be saved thusly:
saveString = "{}{}_{}-{}_{}-{}".format(imgPath,
                                       imgName,
                                       currentTime.tm_min,
                                       currentTime.tm_hour,
                                       currentTime.tm_mday,
                                       currentTime.tm_mon,
                                       currentTime.tm_year)

#get the type of drawing to do from the command line argument:
if len(sys.argv) > 1:
    drawRoutineName = sys.argv[1]
else:
    drawRoutineName = "circles"

#setup logging:
LOGLEVEL = logging.DEBUG
logFileName = "log.{}".format(drawRoutineName)
logging.basicConfig(filename=logFileName,level=LOGLEVEL,filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

#setup
surface, ctx, size, n = utils.drawing.setup_cairo(n=N,
                                                  scale=False,
                                                  cartesian=True)

def dist_trans(i, opts, data):
    opts['scale'] -= (data['current_loop'] * 0.5 * i * opts['decrease'])
    opts['speed'] += (data['current_loop'] * 0.5 * i * opts['increase'])
    return opts

#Drawing:
# create the drawing object
d_o = cp.PDraw(ctx, (size, size), surface)
d_o.register_call('random', cp.calls.random.simple_random_call)
d_o.register_call('ease', cp.calls.easing.run_easing)
d_o.register_call('add_noise', cp.calls.random.additive_noise)
d_o.register_call('pop', cp.calls.value_control.pop_value)

d_o.pipeline([ cp.misc.utils.no_op_layer, {}
               # , cp.dcelp.geometry.create_two_splines, {}
               # , cp.dcelp.geometry.create_points, {}
               # , cp.dcelp.geometry.create_line, {}
               # , cp.dcelp.geometry.create_lines, { 'num' : 15 }
               # , cp.dcelp.geometry.create_grid, { 'num': 10 }
               , cp.dcelp.geometry.create_circle, {}
               , cp.misc.text.text_layer, { 'text' : '' }
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
               , cp.misc.sampling.sample_layer, { 'n' : 500,
                                    'r' : 3,
                                    'colour' : np.array([300, 0.4, 0.4, 0.15]),
                                    'c_type' : 'hsla',
                                    'target' : 'line',
                                    'choice' : 0.05}

               # , cp.misc.skip.skip_layer, { 'type' : 'first', 'not' : True, 'skip_num': 1}
               # , cp.misc.utils.duplicate_layer,  { 'num' : 3}
               # , cp.misc.utils.wiggle_layer, { 'scale' : [0,2],
               #                      'dir' : [0, utils.constants.TWOPI]}

               , cp.colour.hue_rotate, {'easing': 'sigmoid',
                                 'noise_range' : [30,30,-40,-40,25] }

               , cp.colour.hsla_rgba_layer, {}
               , cp.misc.drawing.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                          'clear_type' : 'hsla',
                                          'bbox' : np.array([0,0,size,size]) }

               , cp.misc.skip.skip_layer, { 'type' : 'every',
                                  'count': 1,
                                  'not' : True}
               , cp.misc.utils.set_var_layer, { 'draw': True }

               # , cp.misc.sampling.subsample_layer, { 'n': 1000,
               #                         'sections': 20 }
               , cp.misc.drawing.draw_layer, { 'pixel' : 'circle',
                                          'saveString' : saveString,
                                          'draw'  : True}

               , cp.misc.utils.set_var_layer, { 'clear_colour' : np.array([0,0,0,0]),
                                     'draw' : False}
               , cp.misc.repetition.loop_layer, { 'max_loops' : 7}
               #--------------------
               , cp.misc.repetition.finish_layer, {}
])










# , ul.make_repeat_transform_layer([
               #     nl.displace_layer, {'easing': [('pow_cos_pi', 3.5, [0,1], FULL),
               #                                    ('pow_cos_pi', 3.5, [0,1],  FULL)],
               #                         'scale' : 50,
               #                         'decrease': 3,
               #                         'speed' : 3,
               #                         'increase' : 3,
               #                         'phase' : 0,
               #                         'p_noise' : 0,
               #                         'r_noise' : 0}]), { 'num': 5,
               #
