import cairo
import math
from math import sin,cos
import numpy as np
from numpy import pi
from numpy.random import random
from scipy.interpolate import splprep
from scipy.interpolate import splev
import IPython

#constants:
ALPHA = 0.1
BACKGROUND = [0,0,0,1]
FRONT = [0.8,0.1,0.71,ALPHA]
TWOPI = 2 * pi

def write_to_png(surface,filename,i=None):
    if i:
        surface.write_to_png(filename+"_{}.png".format(i))
    else:
        surface.write_to_png(filename+".png")

def drawRect(ctx,x,y,sx,sy):
    #ctx.set_source_rgba(*FRONT)
    ctx.rectangle(x,y,sx,sy)
    ctx.fill()

#take a position and radius, get a set of random positions on that circle
def sampleCircle(x,y,radius,numOfSteps):
    randI = np.sort(np.random.random(numOfSteps)) * TWOPI
    xPos = x + (np.cos(randI) * radius)
    yPos = y + (np.sin(randI) * radius)
    return np.column_stack((xPos,yPos))
    
def drawCircle(ctx,x,y,r,fill=True):
    ctx.arc(x,y,r,0,TWOPI)
    if fill:
        ctx.fill()
    else:
        ctx.stroke()

def drawDCEL(ctx,dcel):
    ctx.set_source_rgba(0.2,0.2,0.9,1)
    #draw the faces
    draw_dcel_faces(ctx,dcel)
    ctx.set_source_rgba(0.4,0.8,0.1,1)
    #draw edges
    draw_dcel_edges(ctx,dcel)
    ctx.set_source_rgba(0.9,0.1,0.1,1)
    #draw vertices
    draw_dcel_vertices(ctx,dcel)
    
def draw_dcel_faces(ctx,dcel):
    for f in dcel.faces:
        ctx.new_path()
        startEdge = f.outerComponent
        ctx.move_to(startEdge.origin.x,startEdge.origin.y)
        current = startEdge.next
        while current is not startEdge:
            ctx.line_to(current.origin.x,current.origin.y)
            current = current.next
        ctx.close_path()
        ctx.fill()
    
def draw_dcel_edges(ctx,dcel):
    ctx.set_line_width(0.002)
    for e in dcel.halfEdges:
        v1,v2 = e.getVertices()
        ctx.move_to(v1.x,v1.y)
        ctx.line_to(v2.x,v2.y)
        ctx.stroke()
        

def draw_dcel_vertices(ctx,dcel):
    """ Draw all the vertices in a dcel as dots """
    for v in dcel.vertices:
        drawCircle(ctx,v.x,v.y,0.01)
        

def clear_canvas(ctx):
    ctx.set_source_rgba(*BACKGROUND)
    ctx.rectangle(0,0,1,1)
    ctx.fill()
    ctx.set_source_rgba(*FRONT)

#takes array of [[x1,y1]] to smooth
def _interpolate(xy,num_points,smoothing=0.2):
    splineTuple,splineValues = splprep([xy[:,0],xy[:,1]],s=smoothing)
    interpolatePoints = np.linspace(0,1,num_points)
    smoothedXY = np.column_stack(splev(interpolatePoints, splineTuple))
    return smoothedXY

def getDirections(xys):
    #xys.shape = (n,2)
    #convert to vectors:
    #xysPrime.shape = (n,4)
    xysPrime = np.column_stack((xys[1:,:],xys[:-1,:]))
    
    dx = xysPrime[:,2] - xysPrime[:,0]
    dy = xysPrime[:,3] - xysPrime[:,1]

    #radians:
    arc = np.arctan2(dy,dx)
    directions = np.column_stack([np.cos(arc),np.sin(arc)])

    #hypotenuse
    dd = np.sqrt(np.square(dx)+np.square(dy))
    
    return (directions,dd)
    

def granulate(xys,grains=10,mult=2):
    #xys.shape = (n,2)
    #directions.shape = (n,3)
    #dd.shape = (n,)
    directions,dd = getDirections(xys)
    granulated = None
    for i,d in enumerate(dd):
        subGranules = xys[i,:] + (d * directions[i,:]*(np.random.random((grains,1))) * mult)
        if granulated is None:
            granulated = subGranules
        else:
            granulated = np.row_stack((granulated,subGranules))
    return granulated


def vary(xys,stepSize,pix):
    r = (1.0-2.0 * random((len(xys),1)))
    scale = np.reshape(np.arange(len(xys)).astype('float'), (len(xys),1))
    noise = (r*scale*stepSize)
    a = random(len(xys))
    rnd = np.column_stack((np.cos(a), np.sin(a)))
    rndNoise = rnd * noise
    rndNoisePix = rndNoise * pix
    xysPrime = xys + rndNoisePix
    return xysPrime


def sampleAlongLine(x,y,ex,ey,t):
    o_x = (1 - t) * x + t * ex
    o_y = (1 - t) * y + t * ey
    return np.column_stack((o_x,o_y))

def createLine(x,y,ex,ey,t):
    lin = np.linspace(0,1,t)
    line = sampleAlongLine(x,y,ex,ey,lin)

    return line

def bezier1cp(start,cp,end,t):
    samplePoints = np.linspace(0,1,t)
    line1 = createLine(*start,*cp,t)
    line2 = createLine(*cp,*end,t)

    out = sampleAlongLine(line1[:,0],line1[:,1],line2[:,0],line2[:,1],samplePoints)
    return out

def bezier2cp(start,cp1,cp2,end,t):
    samplePoints = np.linspace(0,1,t)
    line1 = createLine(*start,*cp1,t)
    line2 = createLine(*cp1,*cp2,t)
    line3 = createLine(*cp2,*end,t)

    s2cp_interpolation = sampleAlongLine(line1[:,0],line1[:,1],line2[:,0],line2[:,1],samplePoints)
    cp2e_interpolation = sampleAlongLine(line2[:,0],line2[:,1],line3[:,0],line3[:,1],samplePoints)
    out = sampleAlongLine(s2cp_interpolation[:,0],s2cp_interpolation[:,1],cp2e_interpolation[:,0],cp2e_interpolation[:,1],samplePoints)
    
    return out
        

#--------------------
#from pgkelley4's line-segments-intersect on github
def line_segment_intersection(p,pr,q,qs):
    r = pr - p
    s = qs - q

    t = np.cross((q-p),s) / np.cross(r,s)
    u = np.cross((q-p),r) / np.cross(r,s)

    rs = np.cross(r,s)
    qpr = np.cross((q-p),r)

    if rs == 0 or qpr == 0:
        t0 = (q-p) * r / (r * r)
        t1 = t0 + s * r / (r * r)

    elif rs == 0 or qpr != 0:
        return None
    elif rs != 0 and t >= 0 and t <= 1 and u >= 0 and u <= 1:
        return None
    else:
        return None


def get_distance(p1,p2):
    dSquared = pow(p1-p2,2)
    summed = dSquared[:,0] + dSquared[:,1]
    sqrtd = np.sqrt(summed)
    return sqrtd


def get_normal(p1,p2):
    """ Get the normalized direction from two points """
    d = get_distance(p1,p2)
    n = (p1-p2)
    normalized = n / d
    return normalized


def get_bisector(p1,p2,r=False):
    """ With a normalised line, rotate 90 degrees """
    n = get_normal(p1,p2)
    if r:
        nPrime = n.dot([[0,-1],
                        [1 ,0]])
    else:
        nPrime = n.dot([[0 ,1],
                        [-1,0]])
    return nPrime

def get_circle_3p(p1,p2,p3):
    arb_height = 200
    #mid points and norms:
    m1 = get_midpoint(p1,p2)
    n1 = get_bisector(p1,p2,r=True)
    m2 = get_midpoint(p2,p3)        
    n2 = get_bisector(p2,p3,r=True)
    #extended norms:
    v1 = m1 + (1 * arb_height * n1)
    v2 = m2 + (1 * arb_height * n2)
    v1I = m1 + (-1 * arb_height * n1)
    v2I = m2 + (-1 * arb_height * n2)
    #resulting lines:
    l1 = np.column_stack((m1,v1))
    l2 = np.column_stack((m2,v2))
    l1i = np.column_stack((m1,v1I))
    l2i = np.column_stack((m2,v2I))
    #intersect extended norms:
    #in the four combinations of directions
    i_1 = intersect(l1[0],l2[0])
    i_2 = intersect(l1i[0],l2i[0])
    i_3 = intersect(l1[0],l2i[0])
    i_4 = intersect(l1i[0],l2[0])
    #get the intersection:
    the_intersect = [x for x in [i_1,i_2,i_3,i_4] if x is not None]
    if len(the_intersect) != 1:
        return None
    r1 = get_distance(p1,the_intersect[0])
    r2 = get_distance(p2,the_intersect[0])
    r3 = get_distance(p3,the_intersect[0])

    #a circle only if they are have the same radius
    if r1 == r2 and r2 == r3:
        return [the_intersect[0],r1]
    else:
        return None
    


def extend_line(p1,p2,m):
    """ Extend a line by m units """
    n = get_normal(p1,p2)
    el = p1 + (n * m)
    return el

def get_midpoint(p1,p2):
    m = (p1 + p2) / 2
    return m

def rotatePoint(p,cen,rads):
    c = np.cos(rads)
    s = np.sin(rads)
    centred = p - cen
    cosP = centred * c
    sinP = centred * s
    nx = cosP[:,0] - sinP[:,1]
    ny = sinP[:,0] + cosP[:,1]
    unCentred = np.column_stack((nx,ny)) + cen
    return unCentred

def checksign(a,b):
    return math.copysign(a,b) == a

def intersect(l1,l2):
    #From the line intersection stack overflow post
    #The points
    p0 = l1[0:2]
    p1 = l1[2:]
    p2 = l2[0:2]
    p3 = l2[2:]
    #The vectors of the lines
    s1 = p1 - p0
    s2 = p3 - p2
    #origins vectors
    s3 = p0 - p2

    numerator_1 = np.cross(s1,s3)
    numerator_2 = np.cross(s2,s3)
    denominator = np.cross(s1,s2)

    if denominator == 0:
         return None
    
    s = numerator_1 / denominator
    t = numerator_2 / denominator
    
    if 0 < s and s <= 1 and 0 < t and t <= 1:
        return np.array([p0[0] + (t * s1[0]), p0[1] + t * s1[1]])
        
    return None
    
def random_points(n):
    """ utility to get n 2d points """
    return np.random.random(n*2)

def bound_line_in_bbox(line,bbox):
    #todo: take in line, intersect with lines of bbox,
    #replace original line endpoint with intersection point
    return line


def makeHorizontalLine():
    """ Describe a horizontal line as a vector of start and end points  """
    x = random.random()
    x2 = random.random()
    y = random.random()
    if x < x2:    
        return np.array([x,y,x2,y])
    else:
        return np.array([x2,y,x,y])


def makeVerticalLine():
    """ Describe a vertical line as a vector of start and end points """
    x = random.random()
    y = random.random()
    y2 = random.random()
    if y < y2:
        return np.array([x,y,x,y2])
    else:
        return np.array([x,y2,x,y])

def makeParabola(focus,directrix,xs):
    """ Return the xy coords for a given range of xs, with a focus point and bounding line """
    p = Parabola(focus,directrix)
    ys = p(xs)
    xys = np.column_stack((xs,ys))
    return xys


class Parabola(object):
    """ Quadratic Parabola of y = ax^2 + bx + c 
    
    """
    def __init__(focus,directrix):
        self.a = 1/(2* focus[1] - directrix)
        self.b = 0 
        self.c = (focus[1] + directrix) / 2
        
        self.directrix = directrix
        self.focus_x = focus[0]
        self.focus_y = focus[1]

        
    def __call__(self,x):
        axsq = self.a * pow(x - self.focus_x,2)
        bx = self.b * (x - self.focus_x)
        return axsq + bx + self.c
        
                       
