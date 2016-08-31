import numpy as np
from numpy.random import random
from math import pi, sin, cos
import pyqtree
import utils
import IPython

#note to remember:
# spindex = pyqtree.Index(bbox=[0,0,100,100])
# spindex.insert(item=item, bbox=item.bbox)
# matches = spindex.intersect(overlapbbox)

BRANCH_AMNT = 0.1
DELTA = 1 / 100
HALFDELTA = DELTA * 0.5
PI = pi
BALPI = pi - (pi * 0.5)
TWOPI = 2 * PI
COLOUR = [0.2,0.4,0.1,0.4]
LINEPOINTS = 100
RADIUS = 0.002
class Branches(object):

    def __init__(self,ctx,sizeTuple,delta=0.001):
        global DELTA
        self.ctx = ctx
        self.sX = sizeTuple[0]
        self.sY = sizeTuple[1]
        delta = delta
        #branches: an array of np.arrays of shape (n,2)
        self.branches = []
        self.qtree = pyqtree.Index(bbox=[0.0,0.0,1.0,1.0])

    def addBranch(self,x,y):
        """ Register a point pair in the class to grow from """
        self.branches.append(np.array((x,y)))


    def grow(self,i):
        """ Take the frontier, and move it by the delta growth rate in a random direction"""
        #branch updates:
        d_branches = []
        #for each branch, update:
        for i,branch in enumerate(self.branches):
            proposedPoint = (0,0)
            #branch based on point / vector
            if branch.shape[0] > 2:
                proposedPoint = calculateVectorPoint(branch[-2],branch[-1])
            else:
                proposedPoint = calculateSinglePoint(branch[-1])
            #then check for distance to nearby points
            distanceSuccess = checkDistanceFromPoints(proposedPoint,self.qtree)
            if distanceSuccess:
                #insert into the quad tree
                self.qtree.insert(item=1,bbox=makeBBoxFromPoint(proposedPoint,i))
                #insert into the branch
                d_branch = np.row_stack((branch,proposedPoint))
                d_branches.append(d_branch)
                #at random points, create a new branch from the current point
                if random() < BRANCH_AMNT:
                    d_branches.append(np.array([proposedPoint]))
            else:
                d_branches.append(branch)
                    
                    
        #save the branch updates
        self.branches = d_branches


    #Draw the points
    def draw(self):
        self.ctx.set_source_rgba(*COLOUR)
        """ Draw the grown points """
        print("Drawing the branches")
        for branch in self.branches:
            i_branch = np.column_stack((branch[:-1],branch[1:]))
            for i,(x,y,ex,ey) in enumerate(i_branch):
                line = utils.createLine(x,y,ex,ey,LINEPOINTS)
                for xl,yl in line:
                    r = RADIUS * (1 / (i+1))
                    utils.drawCircle(self.ctx,xl,yl,r)
            
            

#------------------------------
#Utilities:
#------------------------------

def calculateSinglePoint(point):
    #only a single point passed in, move in a random direction
    d = np.array([sin(random()*TWOPI),cos(random()*TWOPI)]) * (2 * DELTA)
    return point + d

def calculateVectorPoint(p1,p2):
    #passed in a pair of points, move in the direction of the vector
    #get the direction:
    vector = p2 - p1
    mag = np.sqrt(np.sum(np.square(vector)))
    normalizedVector = vector / mag
    moveVector = normalizedVector * (2 * DELTA)
    jiggledVector = moveVector * np.array([sin(random()*BALPI),cos(random()*BALPI)])
    return p2 + jiggledVector 


def checkDistanceFromPoints(point,quadTree):
    bbox = [point[0] - HALFDELTA,point[1] - HALFDELTA,point[0] + HALFDELTA, point[1] + HALFDELTA]
    area = quadTree.intersect(bbox)
    insideCanvas = point[0] > 0 and point[0] < 1.0 and point[1] > 0 and point[1] < 1.0
    return len(area) == 0 and insideCanvas

def makeBBoxFromPoint(point,i):
    border = HALFDELTA * (1/(i+1))
    return [point[0] - border, point[1] - border, point[0] + border, point[1] + border]
