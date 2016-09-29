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
CIRCLE_COLOUR_INACTIVE = [0,0,1,1]
CIRCLE_RADIUS = 0.005
BEACH_LINE_COLOUR = [0,1,0]
BEACH_LINE_COLOUR2 = [1,1,0]
BEACH_NO_INTERSECT_COLOUR = [1,0,0,1]
BEACH_RADIUS = 0.002
SWEEP_LINE_COLOUR = [0,0,1,1]
LINE_WIDTH = 0.002


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
        #(y_coord, SITE , np.array(xy_coord)) || (y_c, CIRCLE, np.array(xy_c), arc,ACTIVE)
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

        
    def initGraph(self,nodes=None):
        """ Create a graph of initial random sites """
        print("Initialising graph")
        if nodes is None:
            for n in range(self.nodeSize):
                newSite = random.random(2)
                event = SiteEvent(newSite)
                heapq.heappush(self.events,event)
                self.sites.append(event)
        self.dcel = DCEL()
        #Create beachline
        self.beachline = BeachLine()

    def add_circle_event(self,loc,sourceNode,left=True):
        print("Adding circle event: {}".format(loc))
        #if True: #loc[1] > self.sweep_position[0]:
        if left:   
            event = CircleEvent(loc,sourceNode)
        else:
            event = CircleEvent(loc,sourceNode,left=False)
        heapq.heappush(self.events,event)
        self.circles.append(event)

    def delete_circle_event(self,event):
        self.events = [e for e in self.events if not e.nodeIs(event.source)]
        heapq.heapify(self.events)
        event.deactivate()
        
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
        self.update_arcs(self.sweep_position.y())
        #handle the event:
        if type(event) is SiteEvent:
            self.handleSiteEvent(event)
        elif type(event) is CircleEvent:
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
            utils.drawCircle(self.ctx,*site.loc,0.007)
        
        #draw faces

        #draw edge vertices

    def update_arcs(self,d):
        self.beachline.update_arcs(d)
        
        
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
            utils.drawCircle(self.ctx,*site.loc,SITE_RADIUS)

    def draw_circle_events(self):
        for event in self.circles:
            if event.active:
                self.ctx.set_source_rgba(*CIRCLE_COLOUR)
                utils.drawCircle(self.ctx,*event.loc,CIRCLE_RADIUS)
            else:
                self.ctx.set_source_rgba(*CIRCLE_COLOUR_INACTIVE)
                utils.drawCircle(self.ctx,*event.loc,CIRCLE_RADIUS)
                
    def draw_beach_line_components(self):
        #the arcs themselves
        self.ctx.set_source_rgba(*BEACH_LINE_COLOUR,0.1)
        xs = np.linspace(0,1,2000)
        for arc in self.beachline.arcs_added:
            xys = arc(xs)
            for x,y in xys:
                utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)
        #--------------------
        #the frontier:
        #
        # Essentially a horizontal travelling sweep line to draw segments
        #
        self.ctx.set_source_rgba(*BEACH_LINE_COLOUR2,1)
        leftmost_x = 0.0
        ##Get the chain of arcs:
        chain = self.beachline.get_chain()
        if 1 < len(chain):
            enumerated = list(enumerate(chain))
            pairs = zip(enumerated[0:-1],enumerated[1:])
            for (i,a),(j,b) in pairs:
                intersections = a.intersect(b,self.sweep_position.y())
                if len(intersections) == 0:
                    print("NO INTERSECTION: {} - {}".format(i,j))
                    if a.vertical_line:
                        print("A is vertical")
                    if b.vertical_line:
                        print("B is vertical")
                    #Draw the non-intersecting line as red
                    self.ctx.set_source_rgba(*BEACH_NO_INTERSECT_COLOUR)
                    xs = np.linspace(0,1,2000)
                    axys = a(xs)
                    bxys = b(xs)
                    for x,y in axys:
                        utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)
                    for x,y in bxys:
                        utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)
                    self.ctx.set_source_rgba(*BEACH_LINE_COLOUR2,1)
                    continue
                    #raise Exception("No intersection point")
                #intersection xs:
                i_xs = intersections[:,0]
                #xs that are further right than what we've drawn
                valid_xs = i_xs[i_xs>leftmost_x]
                if len(valid_xs) == 0:
                    #nothing valid, try the rest of the arcs
                    continue
                left_most_intersection = valid_xs.min()
                print("Arc {0} from {1:.2f} to {2:.2f}".format(i,leftmost_x,left_most_intersection))
                xs = np.linspace(leftmost_x,left_most_intersection,2000)
                #update the position
                leftmost_x = left_most_intersection
                frontier_arc = a(xs)
                for x,y in frontier_arc:
                    utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)

        if 0 < len(chain) and leftmost_x < 1.0:
            #draw the last arc:
            print("Final Arc from {0:.2f} to {1:.2f}".format(leftmost_x,1.0))
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
        self.ctx.move_to(0.0,sweep_event.y())
        self.ctx.line_to(1.0,sweep_event.y())
        self.ctx.close_path()
        self.ctx.stroke()


    #FORTUNE METHODS
    def handleSiteEvent(self,event):
        #for visualisation: add an arc
        new_arc = Parabola(*event.loc,self.sweep_position.y())
        #if beachline is empty: add and return
        if self.beachline.isEmpty():
            self.beachline.insert_root(new_arc)
            return
                
        #get the x position of the event
        xPos = new_arc.fx
        #search for the breakpoint interval of the beachline
        closest_arc_node = self.beachline.search(xPos)
        
        #remove false alarm circle events
        if closest_arc_node.left_circle_event is not None:
            self.delete_circle_event(closest_arc_node.left_circle_event)
        if closest_arc_node.right_circle_event is not None:
            self.delete_circle_event(closest_arc_node.right_circle_event)
            
        #split the beachline
        new_middle_leaf = self.beachline.split(new_arc,closest_arc_node)
        self.beachline.balance(new_middle_leaf)
        
        #create half edges

        #create circle events:
        self.calculate_circle_events(new_middle_leaf)
        

    def calculate_circle_events(self,node):
        #Generate a circle event for left side, and right side
        left_triple = self.beachline.get_predecessor_triple(node)
        right_triple = self.beachline.get_successor_triple(node)
        #Calculate chords and determine circle event point:
        #add circle event to events and the relevant leaf
        if left_triple:
            left_points = [x.left_arc.get_focus() for x in left_triple]
            left_circle = utils.get_circle_3p(*left_points)
            if left_circle:
                left_circle_loc = utils.get_lowest_point_on_circle(*left_circle)
                self.add_circle_event(left_circle_loc,left_triple[1])

        if right_triple:
            right_points = [x.left_arc.get_focus() for x in right_triple]
            right_circle = utils.get_circle_3p(*right_points)
            if right_circle:
                right_circle_loc = utils.get_lowest_point_on_circle(*right_circle)
                self.add_circle_event(right_circle_loc,right_triple[1],left=False)


    def handleCircleEvent(self,event):
        #remove disappearing arc from tree
        #and update breakpoints
        node = event.source
        pre = node.getPredecessor()
        suc = node.getSuccessor()
        self.beachline.delete_leaf(node)

        if pre.right_circle_event is not None:
            self.delete_circle_event(pre.right_circle_event)
        if suc.left_circle_event is not None:
            self.delete_circle_event(suc.left_circle_event)
        
        #add the centre of the circle as a vertex to DCEL
        
        #recheck for new circle events
        self.calculate_circle_events(pre)
        self.calculate_circle_events(suc)
        

#--------------------
#Event class - For CIRCLE/SITE events

class VEvent(object):

    def __init__(self,site_location):
        self.loc = site_location

    def y(self):
        return self.loc[1]

    def __lt__(self,other):
        return self.y() < other.y()

    def nodeIs(self,other):
        return False
    
class SiteEvent(VEvent):
    def __init__(self,site_loc):
        super().__init__(site_loc)

class CircleEvent(VEvent):
    def __init__(self,site_loc,sourceNode,left=True):
        if left and sourceNode.left_circle_event is not None:
            raise Exception("Trying to add a circle event to a taken node")
        elif not left and sourceNode.right_circle_event is not None:
            raise Exception("Trying to add a circle event to a taken node")
        super().__init__(site_loc)
        self.source = sourceNode
        self.active = True
        self.left = left
        if left:
            sourceNode.left_circle_event = self
        else:
            sourceNode.right_circle_event = self

    def deactivate(self):
        self.active = False
        if self.left:
            self.source.left_circle_event = None
        else:
            self.source.right_circle_event = None
        self.source = None

    def nodeIs(self,node):
        return self.source == node
