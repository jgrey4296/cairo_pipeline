import cairo
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

def drawRect(ctx,x,y,sx,sy):
    ctx.set_source_rgba(*FRONT)
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
        
