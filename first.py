import math
import cairo
import numpy as np
from numpy import pi
from numpy import linspace
from numpy import cos
from numpy import sin

#constants:
BACKGROUND = [0,0,0,1]
FRONT = [1,0,1,0.7]
PIX = 1/1000
R = 0.5
grains = 10
radiusRatio = 5

def draw(ctx):
    clear_canvas(ctx)
    xysa = genPoints()
    drawRects(ctx,xysa)

def clear_canvas(ctx):
    ctx.set_source_rgba(*BACKGROUND)
    ctx.rectangle(0,0,1,1)
    ctx.fill()

def drawRects(ctx,xysa):
    #print('drawing',xys)
    for x,y,sx,sy,a in xysa:
        ctx.set_source_rgba(*FRONT)
        ctx.rectangle(x,y,sx,sy)
        ctx.fill()

def genPoints():
    amnt = 1000
    r = 0.1
    minScale = 1 - 1./radiusRatio
    maxScale = 1 + 1./radiusRatio
    source = np.random.ranf(amnt) * (2*pi)
    xPos = cos(source) #shape : (1000,)
    yPos = sin(source)
    xy = np.column_stack((xPos,yPos)) #shape (1000,2)
    scaleArray = np.linspace(minScale,maxScale,len(xy))
    xy *= np.column_stack((scaleArray,scaleArray))*r
    xy += 0.5
    size = np.ones(amnt) * PIX
    xys = np.column_stack((xy,size,size))
    alpha = np.random.ranf(amnt)
    xysa = np.column_stack((xys,alpha))
    return xysa
    

        


