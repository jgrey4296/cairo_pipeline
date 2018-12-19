"""
Module that Implements a Hyphae like growth algorithm
"""
import numpy as np
from numpy.random import random
from math import pi, sin, cos
import pyqtree
import cairo_utils as utils
import IPython
from simple_draw import SimpleDraw
#note to remember:
# spindex = pyqtree.Index(bbox=[0, 0, 100, 100])
# spindex.insert(item=item, bbox=item.bbox)
# matches = spindex.intersect(overlapbbox)

BRANCH_AMNT = 0.1
DELTA = 1 / 100
HALFDELTA = DELTA * 0.5
PI = pi
BALPI = pi - (pi * 0.5)
TWOPI = 2 * PI
COLOUR = [0.2, 0.4, 0.1, 0.4]
LINEPOINTS = 100
RADIUS = 0.002
NODE_NUM = 100
NODE_RECIPROCAL = 1 / NODE_NUM

class Branches(object):
    """ Grow branches from specified start points """

    def __init__(self, ctx, sizeTuple, delta=0.001):
        global DELTA
        delta = delta
        self.ctx = ctx
        self.sX = sizeTuple[0]
        self.sY = sizeTuple[1]

        #nodes:
        self.nodes = np.zeros((NODE_NUM, NODE_NUM))
        self.frontier = []
        self.paths = []
        self.nextPathIndex = 0
        self.qtree = pyqtree.Index(bbox=[0.0, 0.0, 1.0, 1.0])

    def addBranch(self, x=50, y=50):
        """ Register a point pair in the class to grow from """
        self.nodes[x][y] = 1.0
        self.frontier.append((self.nextPathIndex, x, y))
        self.nextPathIndex += 1
        self.paths.append([(x, y)])

    def grow(self, j):
        """ Take the frontier, and move it by the delta growth rate in a random direction"""
        newFrontier = []
        for (i, x, y) in self.frontier:
            neighbours = self.getOpenNeighbours(x, y)
            if len(neighbours) == 0:
                continue

            choiceIndex = np.random.choice(np.arange(len(neighbours)))
            choice = neighbours[choiceIndex]
            nx = choice[0]
            ny = choice[1]
            if nx < 0 or nx > NODE_NUM or ny < 0 or ny > NODE_NUM:
                #out of bounds, skip
                continue
            #TODO: check the move doesnt cross an existing diagonal

            #claim the node
            self.nodes[nx][ny] = 1.0
            #add to the path
            self.paths[i].append((nx, ny))
            #update the new frontier
            newFrontier.append((i, nx, ny))

            #branch?
            if np.random.random() < BRANCH_AMNT:
                newFrontier.append((self.nextPathIndex, nx, ny))
                self.nextPathIndex += 1
                self.paths.append([(nx, ny)])

        #take the new frontier, apply to old
        self.frontier = newFrontier


    #Draw the points
    def draw(self):
        #print(self.paths)
        """ Draw the grown points """
        self.ctx.set_source_rgba(*COLOUR)
        for path in self.paths:
            prevPoint = None
            for (x, y) in path:
                point = nodeToPosition(x, y)
                if prevPoint is None:
                    utils.drawCircle(self.ctx, point[0], point[1], RADIUS)
                    prevPoint = point
                else:
                    line = utils.createLine(prevPoint[0], prevPoint[1], point[0], point[1], 100)
                    for lx, ly in line:
                        utils.drawCircle(self.ctx, lx, ly, RADIUS)
                    prevPoint = point


    def getOpenNeighbours(self, x, y):
        """ Get the open neighbours of the specified point """
        graph = self.nodes
        neighbours = [
            #[-1, -1], #top left
            [0, -1], #top
            #[1, -1], #top right
            [-1, 0], #left
            [1, 0], #right
            #[-1, 1, ], #bot left
            [0, 1], #bot
            #[1, 1]#bot right
        ]
        openNeighbours = [(x+nx, y+ny) for nx, ny in
                          neighbours if x+nx >= 0 and x+nx < NODE_NUM
                          and y+ny >= 0 and y+ny < NODE_NUM
                          and  graph[x+nx][y+ny] == 0.0]
        return openNeighbours
