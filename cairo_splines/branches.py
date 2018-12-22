"""
Module that Implements a Hyphae like growth algorithm
"""
import numpy as np
from numpy.random import random
from math import pi, sin, cos
import pyqtree
import networkx as nx

import cairo_utils as utils
from cairo_utils.constants import PI, TWOPI, QUARTERPI
from simple_draw import SimpleDraw
#note to remember:
# spindex = pyqtree.Index(bbox=[0, 0, 100, 100])
# spindex.insert(item=item, bbox=item.bbox)
# matches = spindex.intersect(overlapbbox)

NEIGHBOURS = np.array([
    #[-1, -1], #top left
    [0, -1], #top
    #[1, -1], #top right
    [-1, 0], #left
    [1, 0], #right
    #[-1, 1, ], #bot left
    [0, 1], #bot
    #[1, 1]#bot right
])

class Branches(SimpleDraw):
    """ Grow branches from specified start points """

    def __init__(self, ctx, size_tuple):
        super().__init__(self, ctx, size_tuple)
        self.ctx = ctx
        self.size = size_tuple

        # VARIABLES
        self.branch_amnt = 0.1
        self.delta = 1 / 100
        self.half_delta = delta * 0.5
        self.bal_pi = pi - (pi * 0.5)
        self.linepoints = 100
        self.radius = 0.002
        self.node_num = 100
        self.node_reciprocal = 1 / node_num
        self.num_start_points = 5
        self.__next_node = 0

        # Occupied locations grid:
        self.grid = np.zeros((self.node_num, self.node_num), dtype=int)
        # Paths graph
        self.paths = nx.Graph()
        # Nodes index
        self.nodes = {}

    def make_node(self, xy):
        """ Make a single node, adding it to the grid, graph, and index """
        node = { 'i': self.__next_node, 'loc' : xy }
        assert(xy[0] >= 0 and xy[0] < node_num and xy[1] >= 0 and xy[1] < node_num)
        assert(self.grid[xy[0],xy[1]] == 0)
        self.nodes[self.__next_node] = node
        #claim the grid location
        self.grid[xy[0],xy[1]] = self.__next_node
        #add the node to the graph
        self.paths.add_node(self.__next_node)
        # increment the node identifier
        self.__next_node += 1
        return node['i']

    def generate(self, locations=None):
        """ Initialise the drawing """
        #if locations is not none:
        #add locations
        if locations is not None:
            #generate

        assert(isinstance(locations, np.ndarray))
        assert(locations.shape[1] == 2)
        for xy in locations:
            #make the node
            self._initial_condition.append(self.make_node(xy))

    def iterate(self, i, frontier=None):
        """ Grow the frontier """
        new_frontier = []
        for i in frontier:
            assert(i in self.nodes)
            curr_node = self.nodes[i]
            neighbours = self.get_open_neighbours(curr_node['loc'])
            if len(neighbours) == 0:
                continue

            choice_index = np.random.choice(np.arange(len(neighbours)))
            choice_xy = neighbours[choice_index]
            #TODO: check the move doesnt cross an existing diagonal

            #claim the node
            new_i = self.create_node(choice_xy)

            #add to the path
            self.paths.add_edge(curr_node['i'], new_i)
            #update the new frontier
            new_frontier.append(new_i)

            #branch?
            if np.random.random() < BRANCH_AMNT:
                new_frontier.append(curr_node['i'])

        return new_frontier


    def draw(self):
        #print(self.paths)
        """ Draw the grown points """
        self.ctx.set_source_rgba(*COLOUR)
        for path in self.paths:
            prevPoint = None
            for (x, y) in path:
                point = utils.math.nodeToPosition(x, y)
                if prevPoint is None:
                    utils.drawCircle(self.ctx, point[0], point[1], RADIUS)
                    prevPoint = point
                else:
                    line = utils.createLine(prevPoint[0], prevPoint[1], point[0], point[1], 100)
                    for lx, ly in line:
                        utils.drawCircle(self.ctx, lx, ly, RADIUS)
                    prevPoint = point


    def get_open_neighbours(self, xy):
        """ Get the open neighbours of the specified point """
        graph = self.grid
        unchecked_neighbours = xy + NEIGHBOURS
        in_bounds_min = (unchecked_neighbours >= 0).all(axis=1)
        in_bounds_max = (unchecked_neighbours <= self.node_num).all(axis=1)
        valid_neighbours = unchecked_neighbours[(in_bounds_min * in_bounds_max)]
        open_neighbours = valid_neighbours[graph[valid_neighbours[:,0],
                                                 valid_neighbours[:,1]] == 0]

        return open_neighbours
