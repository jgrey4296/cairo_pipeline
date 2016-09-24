import numpy as np
import numpy.random as random
from numpy.linalg import det
import math
from math import pi, sin, cos
import math
import pyqtree
import utils
import IPython
import heapq

from Parabola import Parabola
#from Tree import Tree
from rbtree import RBTree

from dcel import DCEL

#COLOURS:
COLOUR = [0.2,0.1,0.6,1.0]
COLOUR_TWO = [1.0,0.2,0.4,0.5]
SITE_COLOUR = [1,0,0,1]
SITE_RADIUS = 0.002
CIRCLE_COLOUR = [1,1,0,1]
CIRCLE_RADIUS = 0.003
BEACH_LINE_COLOUR = [0,1,0,1]
BEACH_RADIUS = 0.002
SWEEP_LINE_COLOUR = [0,0,1,1]
LINE_WIDTH = 0.002

#event enum:
SITE = 0
CIRCLE = 1

class Voronoi(object):
    """ Creates a random selection of points, and step by step constructs
        a voronoi diagram
    """
    def __init__(self,ctx,sizeTuple,num_of_nodes=10):
        self.ctx = ctx
        self.sX = sizeTuple[0]
        self.sY = sizeTuple[1]
        self.nodeSize = num_of_nodes
        #Heap of tuples of site/circle events
        #(y_coord, SITE , np.array(xy_coord)) || (y_c, CIRCLE, np.array(xy_c))
        self.events = []
        #backup of the original sites
        self.sites = []
        #backup of all circle events
        self.circles = []
        #The beach line
        self.beachline = None
        #The sweep line position
        self.sweep_position = None
        #The output voronoi diagram as a DCEL
        self.dcel = None

        #activated arcs:
        self.activated_arcs = []

        
    def initGraph(self,nodes=None):
        """ Create a graph of initial random sites """
        print("Initialising graph")
        if nodes is None:
            for n in range(self.nodeSize):
                newSite = random.random(2)
                siteDescription = (newSite[1],SITE,newSite)
                heapq.heappush(self.events,siteDescription)
                self.sites.append(newSite)
        self.dcel = DCEL()
        self.beachline = RBTree()
        
    def calculate(self):
        """ Calculate the next step of the voronoi diagram """
        if len(self.events) == 0: #finished calculating
            return False
        print("Calculating step")
        ##handle site / circle event
        event = heapq.heappop(self.events)
        #update the sweep position
        self.sweep_position = event
        #update the arcs:
        self.update_arcs(self.sweep_position[0])
        #handle the event:
        if isSiteEvent(event):
            self.handleSiteEvent(event)
        elif isCircleEvent(event):
            self.handleCircleEvent(event)
        else:
            raise Exception("Unrecognised Event")
        return True 

    def finalise_DCEL(self):
        print("Finalising DCEL")
        #take remaining points in tree, convert to bounded edges

        #traverse DCEL to create faces

        return self.dcel
    
                    
    def draw_voronoi_diagram(self):
        """ Draw the final diagram """
        print("Drawing final voronoi diagram")
        utils.clear_canvas(self.ctx)
        self.ctx.set_source_rgba(*COLOUR)
        
        #draw sites
        for site in self.sites:
            utils.drawCircle(self.ctx,*site,0.007)
        
        #draw faces

        #draw edge vertices

    def update_arcs(self,d):
        for arc in self.activated_arcs:
            arc.update_d(d)
        
        
    #UTILITY DRAW METHODS:
    def draw_intermediate_states(self):
        print("Drawing intermediate state")
        utils.clear_canvas(self.ctx)
        self.draw_sites()
        self.draw_beach_line_components()
        self.draw_sweep_line()
        self.draw_circle_events()
        
    def draw_sites(self):
        self.ctx.set_source_rgba(*SITE_COLOUR)
        for site in self.sites:
            utils.drawCircle(self.ctx,site[0],site[1],SITE_RADIUS)

    def draw_circle_events(self):
        self.ctx.set_source_rgba(*CIRCLE_COLOUR)
        for event in self.circles:        
            utils.drawCircle(self.ctx,site[0],site[1],CIRCLE_RADIUS)
            
    def draw_beach_line_components(self):
        self.ctx.set_source_rgba(*BEACH_LINE_COLOUR)
        xs = np.linspace(0,1,2000)
        for arc in self.activated_arcs:
            xys = arc(xs)
            for x,y in xys:
                utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)
        

    def draw_sweep_line(self):
        if self.sweep_position is None:
            return        
        self.ctx.set_source_rgba(*SWEEP_LINE_COLOUR)
        self.ctx.set_line_width(LINE_WIDTH)
        #a tuple
        sweep_event = self.sweep_position
        self.ctx.move_to(0.0,sweep_event[2][1])
        self.ctx.line_to(1.0,sweep_event[2][1])
        self.ctx.close_path()
        self.ctx.stroke()


    #FORTUNE METHODS
    def handleSiteEvent(self,event):
        #for visualisation: add an arc
        new_parabola = Parabola(event[2][0],event[2][1],self.sweep_position[0])
        self.activated_arcs.append(new_parabola)
        #if beachline is empty: add and return
        if self.beachline.isEmpty():
            new_beach_node = BeachLineNode(new_parabola)
            self.beachline.insert(new_parabola)
            return
                
        #get the x position of the event
        xPos = event[2][0]
        #search for the breakpoint interval of the beachline
        #closest_arc = self.beachline.nearest_node(xPos)
        
        #remove false alarm breakpoints
                
        #split the beachline

        #create half edges

        #check for a circle event / insert a circle event

        
        return None

    def handleCircleEvent(self,event):
        #remove disappearing arc from tree
        #update breakpoints
        #add the centre of the circle as a vertex to DCEL
        #recheck for new circle events
        return None
    
    
#--------------------
#Utilities:

def isSiteEvent(e):
    """ Test an event from the pqueue for site/circle type """
    return e[1] == SITE

def isCircleEvent(e):
    return not isSiteEvent(e)

#----------
#The node to store in the balanced tree:
class BeachLineNode(object):

    def __init__(self,arc,arc2=None):
        #the 1 or 2 arcs that make up the node
        #1 if a leaf, 2 if an interior node
        self.left_arc = arc
        self.right_arc = arc2
        #the circle events that are related to the node
        self.circle_events = []

    def update_arcs(self,d):
        if self.left_arc:
            self.left_arc.update_d(d)
        if self.right_arc:
            self.right_arc.update(d)
        
    def compare(self,xPos,favourLeft=True,new_d=None):
        """
        Given a position, calculate the intersection points of the arcs,
        favouring the (!)left breakpoint if there are two
        returns  -1 | 1 for left | right child to explore
        return 0 for no intersection
        if given a new_d, runs a directrix update on the arcs
        """
        if new_d:
            self.update_arcs(new_d)
            
        return -1
