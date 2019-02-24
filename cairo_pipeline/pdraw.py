"""
A Drawing Class that takes a defined pipeline and draws it
"""

import numpy as np
from itertools import islice
import cairo_utils as utils
import IPython
from . import constants

import logging as root_logger
logging = root_logger.getLogger(__name__)

class PDraw:
    """ Draws a Pipeline of operations """

    def __init__(self, ctx, sizeTuple, surface, imgPath):
        assert(ctx is not None)
        assert(sizeTuple is not None)
        assert(surface is not None)
        assert(isinstance(sizeTuple, tuple) and len(sizeTuple) == 2)
        self._ctx = ctx
        self._surface = surface
        self._size = sizeTuple
        self._center = (sizeTuple[0] * 0.5, sizeTuple[1] * 0.5)
        #More Complex shapes
        self._geometry = {
            'points' : np.zeros((1,utils.constants.SAMPLE_DATA_LEN)),
            'line' : np.zeros((1,utils.constants.LINE_DATA_LEN)),
            # [p1, cp1, cp2, p2]
            'bezier' : np.zeros((1,utils.constants.BEZIER_DATA_LEN)),
        # [p, min_radius, max_radius, min_rads, max_rads]
            'circle' : np.zeros((1,utils.constants.CIRCLE_DATA_LEN))
        }
        self._sampled_geometry = {
            'line' : np.zeros((1,utils.constants.LINE_DATA_LEN)),
            # [p1, cp1, cp2, p2]
            'bezier' : np.zeros((1,utils.constants.BEZIER_DATA_LEN)),
            # [p, min_radius, max_radius, min_rads, max_rads]
            'circle' : np.zeros((1,utils.constants.CIRCLE_DATA_LEN))
        }
        #additional data
        self._current = np.zeros((1, utils.constants.SAMPLE_DATA_LEN))
        self._samples = np.zeros((1,utils.constants.SAMPLE_DATA_LEN))
        self._text = []
        #Registered crosscuts
        self._registered_crosscuts= {}
        self._crosscut_states = {
            'default' : {}
            }

        # Lookup of Objects associated with basic data
        # eg: _nodes['_core_verts'][1] can hold an object associated with _core_verts[0]
        self._nodes = {}
        # Location to save images:
        self._imgPath = imgPath
        # Debug flag for layers:
        self._debug= False

    def register_crosscuts(self, pairs, namespace=None, start_state=None):
        """ Registers a crosscut function, and its personal data store """
        if namespace is None:
            namespace = "default"
        else:
            if start_state is None:
                start_state = {}
            if namespace not in self._crosscut_states:
                self._crosscut_states[namespace] = start_state
        pairs = { "{}_{}".format(namespace,k) : v for k,v in pairs.items() }
        self._registered_crosscuts.update(pairs)

    def has_crosscut(self, key, namespace=None):
        if namespace is None:
            namespace = "default"
        full_name = "{}_{}".format(namespace, key)
        return full_name in self._registered_crosscuts

    def call_crosscut(self, name, **kwargs):
        """ Calls a registered crosscut by name, with a dictionary of arguments, and its personal state
        The call returns the result of the calculation, and an updated personal state """
        namespace = "default"
        if 'namespace' in kwargs:
            namespace = kwargs['namespace']
        name = "{}_{}".format(namespace,name)
        state = self._crosscut_states[namespace]
        func = self._registered_crosscuts[name]
        result, new_state, new_data = func(self, kwargs, state)
        self._crosscut_states[namespace] =  new_state
        return (result, new_data)

    def crosscut(self, name, **kwargs):
        return self.call_crosscut(name, kwargs)

    def crosscut_state(self, name):
        return self._registered_crosscuts[name][1]

    def pipeline(self, pipelines, max_loops=10):
        """ Transforms the drawing in a set of steps """
        data = { 'current_step' : 0,
                 'finish' : False,
                 'current_loop' : 0,
                 'max_loops' : max_loops,
                 'bbox' : np.array([0,0, *self._size])}
        pipe_pairs = list(zip(islice(pipelines, 0, len(pipelines), 2),
                              islice(pipelines, 1, len(pipelines), 2)))
        pipeline_length = len(pipe_pairs)
        while data['current_step'] < pipeline_length and not data['finish']:
            #####
            x, opts = pipe_pairs[data['current_step']]
            if hasattr(x, '__name__'):
                logging.info("Running Layer: ({}) {}".format(len(self._samples), x.__name__))
            else:
                logging.info("Running Anonymous Layer")
            data = x(self, opts, data)
            data['current_step'] += 1
            ####

        return data

    #------------------------------
	# def Draw Primitives
	#------------------------------

    def add_points(self, points):
        """ Add 2 dimensional points to the data to draw,
        points: np.array([[x,y,r]])
        """
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == utils.constants.SAMPLE_DATA_LEN)
        self._geometry['point'] = np.row_stack((self._geometry['point'], points))

    def add_lines(self, lines):
        """ Add lines to sample then draw
        lines: np.array([[x,y,x,y]])
        """
        assert(isinstance(lines, np.ndarray))
        assert(lines.shape[1] == utils.constants.LINE_DATA_LEN)
        self._geometry['line'] = np.row_stack((self._geometry['line'],
                                               lines))

    def add_bezier(self, beziers):
        """ Add 2 cp bezier curves to sample then draw
        beziers: np.array([[x1,y1,cx1, cy1, cx2, cy2, x2, y2]])
        """
        assert(isinstance(beziers, np.ndarray))
        assert(beziers.shape[1] == utils.constants.BEZIER_DATA_LEN)
        self._geometry['bezier'] = np.row_stack((self._geometry['bezier'],
                                                 beziers))

    def add_circle(self, circles):
        """ Add circles to sample then draw
        Circles: np.array([[x,y, rad_min, rad_max, radius_min, radius_max]])
        """
        assert(isinstance(circles, np.ndarray))
        assert(circles.shape[1] == utils.constants.CIRCLE_DATA_LEN)
        self._geometry['circle'] = np.row_stack((self._geometry['circle'],
                                                 circles))

    def add_text(self, text, position, size, colour):
        """ Adds text on top of the drawing """
        self._text.append((text,position,size, colour))

    #------------------------------
    # def Implemented Drawing:
    #------------------------------

    def draw_text(self):
        for (t,p,s,c) in self._text:
            self._ctx.set_font_size(s)
            self._ctx.set_source_rgba(*c)
            utils.drawing.draw_text(self._ctx, p, t)


    #------------------------------
    # def Node Utilities
    #------------------------------
    def lookup(self, group, index, missing=None):
        self.create_group(group)
        if index in self._nodes[group]:
            return self._nodes[group][index]
        if missing is None:
            missing = {}
        if callable(missing):
            missing = missing()
        self._nodes[group][index] = missing
        return missing

    def create_group(self, group):
        if group in self._nodes:
            return
        self._nodes[group] = {}
