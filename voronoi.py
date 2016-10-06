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
import pickle
from string import ascii_uppercase

from Parabola import Parabola
from beachline import BeachLine,Left,Right,Centre

from dcel import DCEL

import logging


#SAVE FILE:
SAVENAME = "graph_data.pkl"

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

currentStep = 0

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

    def save_graph(self,values):
        with open(SAVENAME,'wb') as f:
            pickle.dump(values,f)
        
    def load_graph(self):
        with open(SAVENAME,'rb') as f:
            return pickle.load(f)

        
    def initGraph(self,data=None):
        """ Create a graph of initial random sites """
        logging.info("Initialising graph")
        values = data
        if values is None:
            for n in range(self.nodeSize):
                newSite = random.random(2)
                if values is None:
                    values = np.array([newSite])
                else:
                    values = np.row_stack((values,newSite))

        for site in values:
            event = SiteEvent(site)
            heapq.heappush(self.events,event)
            self.sites.append(event)
        self.dcel = DCEL()
        #Create beachline
        self.beachline = BeachLine()
        return values
        

    def add_circle_event(self,loc,sourceNode,left=True):
        if loc[1] < self.sweep_position.y() or np.allclose(loc[1],self.sweep_position.y()):
            logging.warning("Breaking out of add circle event: at/beyond sweep position")
            return
        #if True: #loc[1] > self.sweep_position[0]:
        if left:   
            event = CircleEvent(loc,sourceNode,i=currentStep)
        else:
            event = CircleEvent(loc,sourceNode,left=False,i=currentStep)
        logging.info("Adding: {}".format(event))
        heapq.heappush(self.events,event)
        self.circles.append(event)

    def delete_circle_event(self,event):
        logging.info("Deleting Circle Event: {}".format(event))
        #self.events = [e for e in self.events if not e.nodeIs(event.source)]
        #heapq.heapify(self.events)
        event.deactivate()
        
    def calculate(self,i):
        """ Calculate the next step of the voronoi diagram """
        global currentStep
        currentStep = i
        if len(self.events) == 0: #finished calculating
            return False
        ##handle site / circle event
        event = heapq.heappop(self.events)
        #update the sweep position
        self.sweep_position = event
        logging.info("Sweep position: {}".format(self.sweep_position.loc))
        #update the arcs:
        self.update_arcs(self.sweep_position.y())
        #handle the event:
        if isinstance(event,SiteEvent):
            self.handleSiteEvent(event)
        elif isinstance(event,CircleEvent):
            if event.active:
                self.handleCircleEvent(event)
            else:
                logging.warning("-------------------- Skipping deactivated circle event")
                print(event)
        else:
            raise Exception("Unrecognised Event")
        return True 

    def finalise_DCEL(self):
        logging.info("Finalising DCEL")
        #take remaining points in tree, convert to bounded edges

        #traverse DCEL to create faces

        return self.dcel
    
                    
    def draw_voronoi_diagram(self):
        """ Draw the final diagram """
        logging.info("Drawing final voronoi diagram")
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
        logging.info("Drawing intermediate state")
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
        leftmost_x = math.nan
        ##Get the chain of arcs:
        chain = self.beachline.get_chain()
        if len(chain) > 1:
            enumerated = list(enumerate(chain))
            pairs = zip(enumerated[0:-1],enumerated[1:])
            for (i,a),(j,b) in pairs:
                logging.debug("Drawing {} -> {}".format(a,b))
                intersections = a.value.intersect(b.value,self.sweep_position.y())
                #print("Intersections: ",intersections)
                if len(intersections) == 0:
                    logging.exception("NO INTERSECTION: {} - {}".format(i,j))
                    #Draw the non-intersecting line as red
                    self.ctx.set_source_rgba(*BEACH_NO_INTERSECT_COLOUR)
                    xs = np.linspace(0,1,2000)
                    axys = a.value(xs)
                    bxys = b.value(xs)
                    for x,y in axys:
                        utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)
                    for x,y in bxys:
                        utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)
                    self.ctx.set_source_rgba(*BEACH_LINE_COLOUR2,1)
                    continue
                    #----------
                    #raise Exception("No intersection point")
                #intersection xs:
                i_xs = intersections[:,0]
                #xs that are further right than what we've drawn
                if leftmost_x is math.nan:
                    valid_xs = i_xs
                else:
                    valid_xs = i_xs[i_xs>leftmost_x]
                if len(valid_xs) == 0:
                    #nothing valid, try the rest of the arcs
                    continue
                left_most_intersection = valid_xs.min()
                logging.debug("Arc {0} from {1:.2f} to {2:.2f}".format(i,leftmost_x,left_most_intersection))
                if leftmost_x is math.nan:
                    leftmost_x = left_most_intersection - 1
                xs = np.linspace(leftmost_x,left_most_intersection,2000)
                #update the position
                leftmost_x = left_most_intersection
                frontier_arc = a.value(xs)
                for x,y in frontier_arc:
                    utils.drawCircle(self.ctx,x,y,BEACH_RADIUS)

        if len(chain) > 0 and (leftmost_x is math.nan or leftmost_x < 1.0):
            if leftmost_x is math.nan:
                leftmost_x = 0
            #draw the last arc:
            logging.warn("Final Arc from {0:.2f} to {1:.2f}".format(leftmost_x,1.0))
            xs = np.linspace(leftmost_x,1.0,2000)
            frontier_arc = chain[-1].value(xs)
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
        logging.info("Handling Site Event: {}".format(event))
        #for visualisation: add an arc
        new_arc = Parabola(*event.loc,self.sweep_position.y())
        #if beachline is empty: add and return
        if self.beachline.isEmpty():
            self.beachline.insert(new_arc)
            return
                
        #get the x position of the event
        xPos = new_arc.fx
        #search for the breakpoint interval of the beachline
        closest_arc_node,dir = self.beachline.search(xPos)
        
        logging.info("Closest Arc Triple: {} *{}* {}".format(closest_arc_node.predecessor, closest_arc_node,closest_arc_node.successor))
        logging.info("Direction: {}".format(dir))
        
        #remove false alarm circle events
        if closest_arc_node.left_circle_event is not None:
            self.delete_circle_event(closest_arc_node.left_circle_event)
        if closest_arc_node.right_circle_event is not None:
            self.delete_circle_event(closest_arc_node.right_circle_event)
            
        #split the beachline
        if isinstance(dir,Centre) or isinstance(dir,Right):
            new_node = self.beachline.insert_successor(closest_arc_node,new_arc)
            duplicate_node = self.beachline.insert_successor(new_node,closest_arc_node.value)
        else:
            new_node = self.beachline.insert_predecessor(closest_arc_node,new_arc)
            duplicate_node = self.beachline.insert_predecessor(new_node,closest_arc_node.value)
        newTriple = [closest_arc_node.value.id,new_node.value.id,duplicate_node.value.id]
        tripleString = "-".join([ascii_uppercase[x] for x in newTriple])
        logging.info("Split {} into {}".format(ascii_uppercase[newTriple[0]],tripleString))
            
            
        #create half edges

        #create circle events:
        self.calculate_circle_events(new_node)
        

    def calculate_circle_events(self,node,left=True,right=True):
        logging.info("Calculating circle events for: {}".format(node))
        #Generate a circle event for left side, and right side
        left_triple = self.beachline.get_predecessor_triple(node)
        right_triple = self.beachline.get_successor_triple(node)
        #Calculate chords and determine circle event point:
        #add circle event to events and the relevant leaf
        if left_triple:
            logging.info("Calc Left Triple: {}".format("-".join([str(x) for x in left_triple])))
        if left and left_triple and left_triple[0].value != left_triple[2].value:
            left_points = [x.value.get_focus() for x in left_triple]
            left_circle = utils.get_circle_3p(*left_points)
            if left_circle and not utils.isClockwise(*left_points,cartesian=True):
                left_circle_loc = utils.get_lowest_point_on_circle(*left_circle)
                #check the l_t_p/s arent in this circle
                #note: swapped this to add on the right ftm
                self.add_circle_event(left_circle_loc,left_triple[1],left=False)
            else:
                logging.warn("Left circle response: ", left_circle)

        if right_triple:
            logging.info("Calc Right Triple: {}".format("-".join([str(x) for x in right_triple])))
        if right and right_triple and right_triple[0].value != right_triple[2].value:
            right_points = [x.value.get_focus() for x in right_triple]
            right_circle = utils.get_circle_3p(*right_points)
            if right_circle and not utils.isClockwise(*right_points,cartesian=True):
                right_circle_loc = utils.get_lowest_point_on_circle(*right_circle)
                #note: swapped this to add on the left ftm
                self.add_circle_event(right_circle_loc,right_triple[1])
            else:
                logging.warn("Right circle response: {}".format(right_circle))


    def handleCircleEvent(self,event):
        logging.info("Handling Circle Event: {}".format(event))
        #remove disappearing arc from tree
        #and update breakpoints
        node = event.source
        pre = node.predecessor
        suc = node.successor
        self.beachline.delete(node)

        logging.info("attempting to remove pre-right circle events for: {}".format(pre))
        if pre and pre.right_circle_event is not None:
            self.delete_circle_event(pre.right_circle_event)
        logging.info("Attempting to remove succ-left circle events for: {}".format(suc))
        if suc and suc.left_circle_event is not None:
            self.delete_circle_event(suc.left_circle_event)
        
        #add the centre of the circle as a vertex to DCEL
        
        #recheck for new circle events
        if pre:
            self.calculate_circle_events(pre,left=False)
        if suc:
            self.calculate_circle_events(suc,right=False)
        

#--------------------
#Event class - For CIRCLE/SITE events

class VEvent(object):

    def __init__(self,site_location,i=-1):
        self.loc = site_location
        self.step = i

    def y(self):
        return self.loc[1]

    def __lt__(self,other):
        return self.y() < other.y()

    def nodeIs(self,other):
        return False
    
class SiteEvent(VEvent):
    def __init__(self,site_loc,i=None):
        super().__init__(site_loc,i=i)

    def __str__(self):
        return "Site Event: Loc: {}".format(self.loc)

class CircleEvent(VEvent):
    def __init__(self,site_loc,sourceNode,left=True,i=None):
        if left and sourceNode.left_circle_event is not None:
            raise Exception("Trying to add a circle event to a taken left node: {} : {}".format(sourceNode,sourceNode.left_circle_event))
        elif not left and sourceNode.right_circle_event is not None:
            raise Exception("Trying to add a circle event to a taken right node: {} : {}".format(sourceNode,sourceNode.right_circle_event))
        super().__init__(site_loc,i=i)
        self.source = sourceNode
        self.active = True
        self.left = left
        if left:
            sourceNode.left_circle_event = self
        else:
            sourceNode.right_circle_event = self

    def __str__(self):
        return "Circle Event: {}, Node: {}, Left: {}, Added On Step: {}".format(self.loc,
                                                                                self.source,
                                                                                self.left,
                                                                                self.step)
            
    def deactivate(self):
        self.active = False
        if self.left:
            self.source.left_circle_event = None
        else:
            self.source.right_circle_event = None
        #self.source = None

    def nodeIs(self,node):
        return self.source == node
