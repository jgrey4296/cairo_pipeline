"""
A Layer to Map a variable to a colour
"""
import numpy as np
from functools import partial
import cairo_utils as utils
import IPython
def colour_lookup(d, opts):
    vals = d.call_crosscut('access',
                           lookup={
                               'c_type' : 'hsla',
                               'heightmap' : np.zeros((1,1)),
                               'index' : 0 },
                           opts=opts)
    c_type, heightmap, index = vals
    samples = d._samples
    size = d._size

    colour = samples[:,-utils.constants.COLOUR_SIZE:]
    # rst = samples[:,:utils.constants.COLOUR_SIZE]

    looked_up_values = __interpolate(heightmap, size, samples[:,:2])
    if c_type == 'hsla' and index == 0:
        #scale the values
        looked_up_values = np.interp(looked_up_values, [0,1],[0,360])

    # IPython.embed(simple_prompt=True)
    colour[:,index] = looked_up_values

    # d._samples = np.column_stack((rst, colour))

def __interpolate(heightmap, surface_size, xys):
    heightmap_size = heightmap.shape
    xs = np.interp(xys[:,0], [0, surface_size[0]-1], [0, heightmap_size[0]-1]).astype(int)
    ys = np.interp(xys[:,1], [0, surface_size[1]-1], [0, heightmap_size[1]-1]).astype(int)
    return heightmap[xs,ys]
