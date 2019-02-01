#!/Users/jgrey/anaconda/bin/python
#!/users/jgrey/anaconda/bin/python
import sys
import time
import math
import cairo
import logging
import numpy as np
import cairo_utils as utils
import cairo_splines as cs
import cairo_splines.util_layer as util_layer
import cairo_splines.geometry_generators as gg
import cairo_splines.sand_deformation as sand_deform
import cairo_splines.call_registries as cr
import cairo_splines.colour_pipeline as cp
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
d_o = cs.PDraw(ctx, (size, size), surface)
d_o.register_call('random', cr.simple_random_call)
d_o.register_call('ease', cr.run_easing)
d_o.register_call('add_noise', cr.additive_noise)
d_o.register_call('pop', cr.pop_value)

d_o.pipeline([ util_layer.no_op_layer, {}
               # , gg.create_two_splines, {}
               # , gg.create_points, {}
               # , gg.create_line, {}
               # , gg.create_lines, { 'num' : 15 }
               , gg.create_grid, { 'num': 10 }
               # , gg.create_circle, {}
               , util_layer.text_layer, { 'text' : '' }
               , util_layer.sample_layer, { 'n' : 3000,
                                                 'r' : 3,
                                            'colour' : np.array([300, 0.4, 0.4, 0.15]),
                                            'c_type' : 'hsla',
                                            'target' : 'line',
                                            'choice' : -1}
               #--------------------
               , util_layer.loop_start_layer, {}
               , util_layer.log_layer, { 'message' : 'Loop: {current_loop}' }
               , util_layer.skip_layer, { 'type' : 'first' }
               , util_layer.rgba_hsla_layer, {}
               , sand_deform.test_displace, {'scale': [280, 10, 50, -20, 50, 20, -10] }
               # , util_layer.make_repeat_transform_layer([
               #     sand_deform.displace_layer, {'easing': [('pow_cos_pi', 3.5, [0,1], FULL),
               #                                             ('pow_cos_pi', 3.5, [0,1],  FULL)],
               #                                  'scale' : 50,
               #                                  'decrease': 3,
               #                                  'speed' : 3,
               #                                  'increase' : 3,
               #                                  'phase' : 0,
               #                                  'p_noise' : 0,
               #                                  'r_noise' : 0}]), { 'num': 5,
               #                                                      'transform' : dist_trans}
               # , sand_deform.granulate_layer, {'rad' : [-utils.constants.QUARTERPI,
               #                                          -utils.constants.QUARTERPI+0.4],
               #                                 'mult'  : [200,200],
               #                                 'choice': 0.4}
               # , util_layer.sample_layer, { 'r' : 5,
               #                              'colour' : np.array([101, 0.4, 0.5, 0.02]),
               #                              'target' : 'line',
               #                              'choice' : 0.01}
               # , util_layer.skip_layer, { 'type' : 'first', 'not' : True, 'skip_num': 1}
               # , util_layer.duplicate_layer,  { 'num' : 3}
               # , util_layer.wiggle_layer, { 'scale' : [0,2],
               #                               'dir' : [0, utils.constants.TWOPI]}
               , cp.hue_rotate, {'easing': 'sigmoid',
                                 'noise_range' : [30,30,-40,-40,25] }
               , util_layer.hsla_rgba_layer, {}
               , util_layer.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                                  'clear_type' : 'hsla',
                                                  'bbox' : np.array([0,0,size,size]) }
               , util_layer.skip_layer, { 'type' : 'every',
                                          'count': 1,
                                          'not' : True}
               , util_layer.set_var_layer, { 'draw': True }
               , util_layer.subsample_layer, { 'n': 1000,
                                               'sections': 20 }
               , util_layer.draw_layer, { 'pixel' : 'circle',
                                          'saveString' : saveString,
                                          'draw'  : True}
               , util_layer.set_var_layer, { 'clear_colour' : np.array([0,0,0,0]),
                                             'draw' : False}
               , util_layer.loop_layer, { 'max_loops' : 7}
               #--------------------
               , util_layer.finish_layer, {}
])
