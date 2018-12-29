import numpy as np
import cairo_utils as utils
from .simple_draw import SimpleDraw



def ExamplePipeline(d, pipeline_data):
    """ The simplest pipeline. adds some shapes, and samples """
    assert(isinstance(d, SimpleDraw))

    verts = np.random.random((20,7))
    #scale up the position and radius: ((b - a) * x) + a
    mask = np.array([1,1,1,0,0,0,0], dtype='float64')
    mask *= np.array([d._size[0],d._size[1], d._size[0]*0.01, 0, 0, 0, 0])
    mask += np.array([0,0,0,1,1,1,1])
    points = (verts * mask)
    # d.add_points(points)

    d.add_circle(np.array([[d._center[0], d._center[1],
                               0, utils.constants.TWOPI,
                               200, 800,
                               0,1,1,0.4
    ]]))

    d.add_points(np.array([[d._center[0], d._center[1],300, 1, 0, 0, 0.4],
                              [0,0,150, 0, 0, 1,0.3],
                              [0,d._size[1],150, 0, 0.5, 0.5, 0.3],
                              [d._size[0],0,150, 0.5, 0.5, 0, 0.3]]))

    d.add_bezier(np.array([[d._center[0] - d._size[0]*0.5, d._center[1],
                               d._center[0], d._center[1] + d._size[1]*0.25,
                               d._center[0] + d._size[0]*0.25, d._center[1] - d._size[1]*0.25,
                               d._center[0] + d._size[0]*0.5, d._center[1],
                               1,0.2,0.4,0.1]]))

    d.add_bezier(np.array([[d._center[0] - d._size[0]*0.5, d._center[1],
                               d._center[0], d._center[1] + d._size[1]*0.25,
                               d._center[0] + d._size[0]*0.25, d._center[1] - d._size[1]*0.25,
                               d._center[0] + d._size[0]*0.5, d._center[1],
                               1,0.2,0.4,0.2]]))
    d.sample_shapes(3800, r=3)


    d.add_text("Example Draw", [d._size[0]*0.1, d._size[1]*0.05],
                    d._size[0]*0.02, [1,1,1,1])

    return None
