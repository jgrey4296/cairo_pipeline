import IPython
import cairo
from random import random
from math import atan2, pi,sin,cos
import utils
import numpy as np


surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,2000,2000)
ctx = cairo.Context(surface)
ctx.scale(2000,2000)

utils.clear_canvas(ctx)

focus = [0.5,0.5]

def r2pi():
    return random() * 2 * pi

rs = [r2pi() for x in range(20)]

points = [[0.5+(sin(x)*0.45),0.5+(cos(x)*0.45)] for x in rs]

ctx.set_source_rgba(1,0,0,1)

utils.drawCircle(ctx,focus[0],focus[1],0.009)

rel = [[x-focus[0],y-focus[1],x,y] for x,y in points]
angled = [[atan2(yp,xp),x,y] for xp,yp,x,y in rel]
sortedAngled = sorted(angled,key=lambda x: x[0])

for i,(arc,x,y) in enumerate(sortedAngled):
    ctx.set_source_rgba(1,1-(0.1*i),0.1 * i,1)
    utils.drawCircle(ctx,x,y,0.006)

surface.write_to_png('test_order.png')
