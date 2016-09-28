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
from beachline import BeachLine

from dcel import DCEL

#COLOURS:
COLOUR = [0.2,0.1,0.6,1.0]
COLOUR_TWO = [1.0,0.2,0.4,0.5]
SITE_COLOUR = [1,0,0,1]
SITE_RADIUS = 0.002
CIRCLE_COLOUR = [1,1,0,1]
CIRCLE_RADIUS = 0.003
BEACH_LINE_COLOUR = [0,1,0]
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
        #Create beachline with comparison function
        self.beachline = BeachLine()
        
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
        #the arcs themselves
        # self.ctx.set_source_rgba(*BEACH_LINE_COLOUR,0.5)
        # xs = np.linspace(0,1,2000)
        # for arc in self.activated_arcs:
        #     xys = arc(xs)
        #     for x,y in xys:
        #         utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)

        #the frontier:
        self.ctx.set_source_rgba(*BEACH_LINE_COLOUR,1)
        leftmost_x = 0.0
        ##Get the chain of arcs:
        chain = self.beachline.get_chain()
        if 1 < len(chain):
            enumerated = list(enumerate(chain))
            pairs = zip(enumerated[0:-1],enumerated[1:])
            for (i,a),(j,b) in pairs:
                intersections = a.intersect(b,self.sweep_position[0])
                if len(intersections) == 0:
                    print("NO INTERSECTION: {} - {}".format(i,j))
                    continue
                    #raise Exception("No intersection point")
                left_most_intersection = intersections.min()
                print("Arc {} from {} to {}".format(i,leftmost_x,left_most_intersection))
                xs = np.linspace(leftmost_x,left_most_intersection,2000)
                leftmost_x = left_most_intersection
                frontier_arc = a(xs)
                
                for x,y in frontier_arc:
                    utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)

        if 0 < len(chain):
            #draw the last arc:
            print("Final Arc from {} to {}".format(leftmost_x,"1.0"))
            xs = np.linspace(leftmost_x,1.0,2000)
            frontier_arc = chain[-1](xs)
            for x,y in frontier_arc:
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
        new_arc = Parabola(event[2][0],event[2][1],self.sweep_position[0])
        self.activated_arcs.append(new_arc)
        #if beachline is empty: add and return
        if self.beachline.isEmpty():
            self.beachline.insert_root(new_arc)
            return
                
        #get the x position of the event
        xPos = new_arc.fx
        #search for the breakpoint interval of the beachline
        closest_arc_node = self.beachline.search(xPos,self.sweep_position[0])
        
        #remove false alarm breakpoints
        
        #split the beachline
        new_head = self.beachline.split(new_arc,closest_arc_node)
        self.beachline.balance(new_head)
        
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

