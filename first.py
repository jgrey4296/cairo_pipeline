import math
import cairo
import numpy as np
from numpy import pi
from numpy import linspace
from numpy import cos
from numpy import sin

#constants:
BACKGROUND = [1,1,1,1]
FRONT = [1,0,1]
PIX = 1/1000
R = 0.5
grains = 10
radiusRatio = 5

def draw(ctx,WIDTH,HEIGHT):
    global PIX
    PIX = 0.002 #1./float(WIDTH)
    
    print('PIX %f' % PIX)

    clear_canvas(ctx)
    ctx.set_source_rgba(*[0,0,0,1])
    ctx.rectangle(0.005,0.005,0.99,0.99)
    ctx.fill()

    xysa = genPoints()
    
    drawRects(ctx,xysa)

    
    # for point in xysa:
    #     rand = np.random.ranf(grains * 2) * 0.07 + 1
    #     points = point[:2] * np.resize(rand,(grains,2))
    #     repeatedSA = np.array([point[2:]]).repeat(grains,axis=0)
    #     newXYSA = np.column_stack((points,repeatedSA))
    #     drawRects(ctx,newXYSA)
            
    #drawGradient(ctx)
    #ctx.translate (0.1, 0.1)
    #drawShape(ctx)

def drawGradient(ctx):
    pat = cairo.LinearGradient (0.2, 0.5, 0.2, 0.15)
    pat.add_color_stop_rgba(0.2,0,0,1,1)
    pat.add_color_stop_rgba(0.5,0,1,0,0.2)
    ctx.rectangle (0, 0, 1, 1) # Rectangle(x0, y0, x1, y1)
    ctx.set_source (pat)
    ctx.fill ()

def drawShape(ctx):
    ctx.move_to (0, 0)
    ctx.arc (0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
    ctx.line_to (0.5, 0.1) # Line to (x,y)
    ctx.curve_to (0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
    ctx.close_path ()
    ctx.set_source_rgb (0.3, 0.2, 0.5) # Solid color
    ctx.set_line_width (0.02)
    ctx.stroke ()


def clear_canvas(ctx):
    ctx.set_source_rgba(*BACKGROUND)
    ctx.rectangle(0,0,1,1)
    ctx.fill()

def drawRects(ctx,xysa):
    #print('drawing',xys)
    for x,y,sx,sy,a in xysa:
        ctx.set_source_rgba(*FRONT,a)
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
    

        


