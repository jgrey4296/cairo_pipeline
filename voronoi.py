import numpy as np
import numpy.random as random
from math import pi, sin, cos
import pyqtree
import utils
import IPython

from Tree import Tree

COLOUR = [0.2,0.1,0.6,0.5]
COLOUR_TWO = [1.0,0.2,0.4,0.5]


class Voronoi(object):

    def __init__(self,ctx,sizeTuple,num_of_nodes):
        self.ctx = ctx
        self.sX = sizeTuple[0]
        self.sY = sizeTuple[1]
        self.nodeSize = num_of_nodes
        #Nodes: Array of n horizontal and vertical lines
        self.graph = np.zeros((1,4))
        self.intersections = np.zeros((1,2))
        
    def initGraph(self):
        #insert a bunch of horizontal or vertical lines
        for x in range(self.nodeSize):
            choice = random.choice(['h','v'])
            if choice == 'h':
                self.graph = np.row_stack((self.graph,makeHorizontalLine()))
            else:
                self.graph = np.row_stack((self.graph,makeVerticalLine()))

    def calculate(self):
        tree = Tree(0.5)
        active = []
        #separate into events
        events = self.graphToEvents()
        
        #go through each event:
        for e in events:
            if len(e) == 3:
                if e[-1] not in active:
                    ## if horizontal start - add to tree
                    active.append(e[-1])
                    tree.insert(e[1],data=e[-1])
                else:
                    ## if horizontal end - remove from tree
                    active.remove(e[-1])
                    v = tree.search(e[1])
                    if v is not None:
                        v.data = None
                    #tree.delete(e[1])
            elif len(e) == 4:
                ## if vertical - get range then search, and store intersections
                r = tree.getRange(e[1],e[2])
                #todo: mark intersections
                line_indices = [x.data for x in r if x.data is not None]
                crossPoints = [(e[0],d.value) for d in r if d.data is not None]
                for xy in crossPoints:
                    self.intersections = np.row_stack((self.intersections,xy))

                    
    def draw(self):
        #DRAW LINES
        self.ctx.set_source_rgba(*COLOUR)
        for (x,y,x2,y2) in self.graph:
            line = utils.createLine(x,y,x2,y2,1000)
            for x,y in line:
                utils.drawCircle(self.ctx,x,y,0.002)

        #DRAW INTERSECTIONS:
        self.ctx.set_source_rgba(*COLOUR_TWO)
        for (x,y) in self.intersections:
            utils.drawCircle(self.ctx,x,y,0.009)

#--------------------
    def graphToEvents(self):
        #return lines turned into events
        events = []
        for i,(x,y,x2,y2) in enumerate(self.graph):
            if x == x2: #vertical
                events.append((x,y,y2,i))
            elif y == y2: #horizontal
                events.append((x,y,i))
                events.append((x2,y,i))
        return sorted(events)

#--------------------

def makeHorizontalLine():
    x = random.random()
    x2 = random.random()
    y = random.random()
    if x < x2:    
        return np.array([x,y,x2,y])
    else:
        return np.array([x2,y,x,y])


def makeVerticalLine():
    x = random.random()
    y = random.random()
    y2 = random.random()
    if y < y2:
        return np.array([x,y,x,y2])
    else:
        return np.array([x,y2,x,y])
