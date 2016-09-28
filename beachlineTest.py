import numpy as np
from numpy.random import random
from beachline import BeachLine
from Parabola import Parabola
import utils
import cairo 

bl = BeachLine()
sweep = 0.8
p1 = np.array([0.25,0.5])
p2 = np.array([0.75,0.6])
p3 = np.array([0.35,0.7])

arc1 = Parabola(*p1,sweep)
arc2 = Parabola(*p2,sweep)
arc3 = Parabola(*p3,sweep)
print('Arc1:',arc1)
print('Arc2:',arc2)
print('Arc3:',arc3)

bl.insert_root(arc1)

node1 = bl.search(p2[0],sweep)

new_head1 = bl.split(arc2,node1)
bl.balance(new_head1)
#bl.delete_leaf(bl.root.getMax())

node2 = bl.search(p3[0],sweep)

new_head2 = bl.split(arc3,node2)
bl.balance(new_head2)
bl.delete_leaf(new_head2.getMax())



surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,500,500)
ctx = cairo.Context(surface)
ctx.scale(500,500)
ctx.set_source_rgba(0,0,0,1)
utils.drawRect(ctx,0,0,1,1)
ctx.set_source_rgba(1,0,0,1)

chain = bl.get_chain()
pairs = zip(chain[:-1],chain[1:])
lmx = 0.0
for a,b in pairs:
    print("A:",a)
    print("B:",b)
    intersections = a.intersect(b,sweep)
    if len(intersections) == 0:
        continue
    ixs = intersections[:,0]
    possiblexs = ixs[ixs>lmx]
    #print("intersections:",intersections)
    if len(possiblexs) == 0:
        continue
    lmi = possiblexs.min()
    #if lmi > 1:
    #   continue
    print('Arc from: {0:.2f} to {1:.2f}'.format(lmx,lmi))
    xs = np.linspace(lmx,lmi,1000)
    lmx = lmi
    arc = a(xs)
    for x,y in arc:
        utils.drawCircle(ctx,x,y,0.005)

if lmx < 1:
    print("Drawing Final")
    print(chain[-2])
    print("Arc from: {0:.2f} to {1:.2f}".format(lmx,1.0))
    ctx.set_source_rgba(0,1,0,1)
    xs = np.linspace(lmx,1.0,1000)
    arc = chain[-2](xs)
    for x,y in arc:
        utils.drawCircle(ctx,x,y,0.005)

utils.drawCircle(ctx,*p1,0.004)
utils.drawCircle(ctx,*p2,0.004)
utils.drawCircle(ctx,*p3,0.004)
utils.write_to_png(surface,'beachline_test')

