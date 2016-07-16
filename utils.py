import cairo
import numpy as np
from numpy import pi
from numpy.random import random
from scipy.interpolate import splprep
from scipy.interpolate import splev
import IPython

#constants:
ALPHA = 0.04
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


def clear_canvas(ctx):
    ctx.set_source_rgba(*BACKGROUND)
    ctx.rectangle(0,0,1,1)
    ctx.fill()
    ctx.set_source_rgba(*FRONT)


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

    arc = np.arctan2(dy,dx)
    directions = np.column_stack([np.cos(arc),np.sin(arc)])

    dd = np.sqrt(np.square(dx)+np.square(dy))
    
    return (directions,dd)
    

def granulate(xys,grains=10,mult=2):
    #xys.shape = (n,2)
    #directions.shape = (n,3)
    #dd.shape = (n,)
    directions,dd = getDirections(xys)
    granulated = None
    for i,d in enumerate(dd):
        subGranules = xys[i,:] + (d + directions[i,:]*(np.random.random((grains,1))) * mult)
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
