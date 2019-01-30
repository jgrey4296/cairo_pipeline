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
import cairo_splines.example_pipeline as e_p
import cairo_splines.sand_deformation as sand_deform
#constants
N = 12
imgPath = "./imgs/"
imgName = "initialTest"
currentTime = time.gmtime()
FONT_SIZE = 0.03
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

#Drawing:
# create the drawing object
draw_obj = cs.PDraw(ctx, (size, size), surface)
draw_obj.pipeline([ util_layer.no_op_layer, {}
                    , e_p.create_line, {}
                    # , e_p.create_lines, { 'num' : 15 }
                    # , e_p.create_grid, { 'num': 10 }
                    # , e_p.create_circle, {}
                    , util_layer.text_layer, { 'text' : '' }
                    , util_layer.sample_layer, { 'n' : 3000,
                                                 'r' : 3,
                                                 'colour' : np.array([100, 0.4, 0.8, 0.05]),
                                                 'target' : 'line',
                                                 'choice' : -1}
                    , util_layer.loop_start_layer, {}
                    , util_layer.log_layer, { 'message' : 'Loop: {current_loop}' }
                    , util_layer.skip_layer, { 'type' : 'first_only' }
                    , util_layer.rgba_hsla_layer, {}
                    , sand_deform.displace_layer, {'easing': ['sigmoid','pow_cos_pi'],
                                                   'scale' : 100,
                                                   'speed' : [-2.2,2.8],
                                                   'phase' : [0.2,3.2 ],
                                                   'noise_mul' : 1.8,
                                                   'override' : True}
                    # , sand_deform.granulate_layer, {'rad' : [-utils.constants.QUARTERPI,
                    #                                          -utils.constants.QUARTERPI+0.4],
                    #                                 'mult'  : [200,200],
                    #                                 'choice': 0.4}
                    # , util_layer.sample_layer, { 'r' : 5,
                    #                              'colour' : np.array([101, 0.4, 0.5, 0.02]),
                    #                              'target' : 'line',
                    #                              'choice' : 0.01}
                    # , sand_deform.displace_layer,    {'channels': 10,
                    #                                      'easing': 'sigmoid',
                    #                                      'scale' : 100,
                    #                                      'speed' : [-2.2,2.8],
                    #                                      'phase' : [0.2,3.2 ],
                    #                                      'noise_mul' : 1.8,
                    #                                      'override' : True}
                    # , util_layer.duplicate_layer,  { 'num' : 10}
                    # , util_layer.wiggle_layer, { 'scale' : [0, 200],
                    #                                 'dir' : [0.8, 1.2]}
                    # , cs.ColourPipeline, {'easing': 'sigmoid',
                    #                       'speed' : 5.01,
                    #                       'scale' : 0.8,
                    #                       'target' : 1,
                    #                       'alpha': 0.1,
                    #                       'base' : 0.2,
                    #                       'rndsig' : [0.1, 0.15],
                    #                       }
                    , util_layer.hsla_rgba_layer, {}
                    , util_layer.clear_canvas_layer, { 'clear_colour' : np.array([0,0,0,1]),
                                                       'clear_type' : 'hsla',
                                                       'bbox' : np.array([0,0,size,size]) }
                    , util_layer.draw_layer, { 'pixel' : 'circle',
                                               'saveString' : saveString,
                                               'draw'  : True}
                    , util_layer.set_var_layer, { 'clear_colour' : np.array([0,0,0,0]) }
                    , util_layer.loop_layer, { 'max_loops' : 10}
                    , util_layer.finish_layer, {}
])
