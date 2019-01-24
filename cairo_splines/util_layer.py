""" Util Layer Pipeline
General Utility pipelines
"""
from functools import partial
from .constants import MAX_LAYER_LOOP
import cairo_utils as utils

def make_repeat_layer(n, layers):
    """ Given a number of times to repeat,
    and a list of layers, create a layer to repeat those layers
    when called in PDraw.pipeline """
    assert(all([callable(x) for x in layers]))
    return partial(_repeat_layer, n, layers)

def _repeat_layer(n, layers, d, opts, data):
    for i in range(n):
        for l in layers:
            data = l(d, data)
    return data

def make_conditional_repeat_layer(cond, layers):
    """ Given a condition, and a list of layers,
    create a layer that when called repeats the layers until
    the condition is true on the pipeline_data """
    assert(all([callable(x) for x in layers]))
    assert(callable(x))
    return partial(_conditional_repeat_layer, cond, layers)

def _conditional_repeat_layer(cond, layers, d, opts, data):
    i = MAX_LAYER_LOOP
    while not cond(data) and i > 0:
        for l in layers:
            data = l(d, data)
        i -= 1
    return data

def sample_layer(d, opts, data):
    d.sample_shapes(opts['n'], types=opts['types'], r=opts['r'])
    data['n'] = opts['n']
    return data

def draw_layer(d, opts, data):
    saveString = opts['saveString']
    drawn = 0
    if 'drawn' in data:
        drawn = data['drawn']

    if 'push' in opts:
         d._ctx.save()
    if 'bkgnd' in opts:
        utils.drawing.clear_canvas(d._ctx, colour=opts['bkgnd'], bbox=opts['bbox'])

    if opts['pixel'] == 'square':
        utils.drawing.draw_rect(d._ctx, d._core_verts)
        utils.drawing.draw_rect(d._ctx, d._samples)
    else:
        utils.drawing.draw_circle(d._ctx, d._core_verts)
        utils.drawing.draw_circle(d._ctx, d._samples)

    d.draw_text()
    if 'push' in opts:
        d._ctx.restore()

    if 'draw' in opts:
        utils.drawing.write_to_png(d._surface, saveString, i=drawn)
        data['drawn'] = drawn + 1
    return data

def text_layer(d, opts, data):
    d.add_text(opts['text'], [d._size[0]*0.1, d._size[1]*0.05],
                    d._size[0]*0.02, [1,1,1,1])


    return data
