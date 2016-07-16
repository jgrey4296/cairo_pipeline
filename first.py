import math
import cairo
from cairo import OPERATOR_SOURCE
import numpy as np
from numpy import pi
from numpy import linspace
from numpy import cos
from numpy import sin
from numpy.random import random
from scipy.interpolate import splprep
from scipy.interpolate import splev
import utils
import IPython

from ssClass import SandSpline
from lineClass import LineSpline

#constants:
PIX = 1/pow(2,10)
op = None
sizeTuple = (3000,3000)
numOfCircles = 10
iterationNum = 30
granulate = True
interpolateGranules = False
interpolate = True
interpolateGrains = False

#top level draw command:
def draw(ctx):
    global op
    op = ctx.get_operator()
    #ctx.set_operator(OPERATOR_SOURCE)
    utils.clear_canvas(ctx)
    init2(ctx)
    init3(ctx)

#------------------------------

def init2(ctx):
    ssInst = SandSpline(ctx,sizeTuple)
    for i in range(numOfCircles):
        print('adding circle:',i)
        ssInst.addCircle()

    for i in range(iterationNum):
        print('step:',i)
        ssInst.step(granulate,interpolateGranules)

    ssInst.draw(interpolate,interpolateGrains)

def init3(ctx):
    lineInst = LineSpline(ctx,sizeTuple)
    for i in range(numOfCircles):
        print('adding line:',i)
        line = [x for x in random(4)]
        lineInst.addLine(*line)

    for i in range(iterationNum):
        print('step:',i,' of ',iterationNum)
        lineInst.step(granulate,interpolateGranules)

    lineInst.draw(interpolate,interpolateGrains)
