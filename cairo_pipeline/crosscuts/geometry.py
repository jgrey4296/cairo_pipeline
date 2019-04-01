"""
An initial geometry generating pipeline layers
"""
import IPython
import numpy as np
from scipy.spatial import ConvexHull
import cairo_utils as utils

NAMESPACE = 'geometry'


def setup_layer(d, opts):
    """ Layer : setups up geometry creation crosscuts

    """
    d.register_crosscuts({ 'access' : access,
                           'call'   : call },
                         namespace=NAMESPACE,
                         start_state=None)
    d.register_crosscuts(opts['pairs'], namespace=NAMESPACE)

    return None

def accessor(d, args, state):
    """ Crosscut :  random accessor

    """
    #get the algorithm
    func = d._registered_crosscuts["{}_{}".format(NAMESPACE, args['key'])]
    value = partial(func, state['state'], params=args['params'])
    return (value, state)

def call(d, args, state):
    """ Crosscut :  call a registered random generator

    """
    #get the algorithm
    func, state = accessor(d, args, state)
    #call it
    values = func(args['shape'])
    return (values, state)


#--------------------------------------------------

def create_two_splines(d, args, state):
    """ Adds 2 splines to the geometry list """
    d.add_bezier(np.array([[d._center[0] - d._size[0]*0.5, d._center[1],
                            d._center[0], d._center[1] + d._size[1]*0.25,
                            d._center[0] + d._size[0]*0.25, d._center[1] - d._size[1]*0.25,
                            d._center[0] + d._size[0]*0.5, d._center[1]]]))

    d.add_bezier(np.array([[d._center[0], d._center[1] - 2000,
                            d._center[0] - 2000, d._center[1] + d._size[1]*0.25,
                            d._center[0] + d._size[0]*0.25, d._center[1] - d._size[1]*0.25,
                            d._center[0] + d._size[0]*0.5, d._center[1] + 2000]]))
    return (value, state)


def create_points(d, args, state):
    """ Creates a number of random points """
    verts = np.random.random((20,7))
    #scale up the position and radius: ((b - a) * x) + a
    mask = np.array([1,1,1,0,0,0,0], dtype='float64')
    mask *= np.array([d._size[0],d._size[1], d._size[0]*0.01, 0, 0, 0, 0])
    mask += np.array([0,0,0,1,1,1,1])
    points = (verts * mask)
    d.add_points(points)
    return (value, state)

def create_circle(d, args, state):
    """ Adds a circle """
    d.add_circle(np.array([[d._center[0], d._center[1],
                               0, utils.constants.TWOPI,
                               800, 800
    ]]))
    return (value, state)


def create_point(d, args, state):
    """ Creates a single point """
    d.add_points(np.array([[d._center[0], d._center[1],300, 1, 0, 0, 0.4],
                           [0,0,150, 0, 0, 1,0.3],
                           [0,d._size[1],150, 0, 0.5, 0.5, 0.3],
                           [d._size[0],0,150, 0.5, 0.5, 0, 0.3]]))
    return (value, state)



def create_lines(d, args, state):
    """ Creates a number of random lines """
    rnd = np.random.random((opts['num'], 4))
    scaled = rnd * [*d._size, *d._size]
    d.add_lines(scaled)
    return (value, state)


def create_grid_lines(d, args, state):
    """ Creates a set of horizontal lines """
    num = opts['num'] + 2
    y_increment = d._size[1] / num
    start = y_increment
    size_arr = np.array(d._size[0]).repeat(num)
    xs_min = size_arr * 0.1
    xs_max = size_arr - xs_min
    ys = np.linspace(start, d._size[1] - y_increment, num)
    lines = np.row_stack((xs_min, ys, xs_max, ys)).T
    d.add_lines(lines)
    return (value, state)


def create_line(d, args, state):
    """ Creates a single line """
    size = d._size
    x_min = size[0] * 0.2
    x_max = size[0] - x_min
    y = size[1] * 0.5
    lines = np.array([[x_min, y, x_max, y]])
    d.add_lines(lines)
    return (value, state)


def create_circle_graph(d, args, state):
    """ Create a circle of nodes connected by lines of radius r  """
    r = opts['r']
    num_nodes = opts['num']
    #create the nodes
    #create the lines
    return (value, state)


def create_circle_grid(d, args, state):
    gridsize = opts['size']
    sX = d._size[0]
    sY = d._size[1]
    circles = np.zeros((1,utils.constants.CIRCLE_DATA_LEN))
    for x in np.linspace(0,1,gridsize):
        for y in np.linspace(0,1,gridsize):
            xs = x * sX
            xy = y * sY
            circles = np.row_stack((circles, np.array([xs, xy, *opts['rad'], *opts['radius']])))
    d.add_circle(circles[1:])
    return (value, state)
