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
from bezierClass import BezierLine

#constants:
PIX = 1/pow(2,10)
op = None
sizeTuple = (3000,3000)
numOfCircles = 10
iterationNum = 40
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
    #initCircles(ctx)
    #initLines(ctx)
    #initSpecificLine(ctx)
    bezierTest(ctx)

#------------------------------

def initCircles(ctx):
    ssInst = SandSpline(ctx,sizeTuple)
    for i in range(numOfCircles):
        print('adding circle:',i)
        ssInst.addCircle()

    for i in range(iterationNum):
        print('step:',i)
        ssInst.step(granulate,interpolateGranules)

    ssInst.draw(interpolate,interpolateGrains)

def initLines(ctx):
    lineInst = LineSpline(ctx,sizeTuple)
    for i in range(numOfCircles):
        print('adding line:',i)
        line = [x for x in random(4)]
        lineInst.addLine(*line)

    for i in range(iterationNum):
        print('step:',i,' of ',iterationNum)
        lineInst.step(granulate,interpolateGranules)

    lineInst.draw(interpolate,interpolateGrains)

def initSpecificLine(ctx):
    lineInst = LineSpline(ctx,sizeTuple)
    lineInst.addLine(0.1,0.5,0.9,0.5)

    for i in range(iterationNum):
        print('step:',i,' of ',iterationNum)
        lineInst.step(granulate,interpolateGranules)

    lineInst.draw(interpolate,interpolateGrains)
    
def bezierTest(ctx):
    bInst = BezierLine(ctx,sizeTuple)
    start = [0.0,0.5]
    cp = [0.4,0.6]
    cp2 = [0.8,0.1]
    end = [1.0,0.5]

    bInst.addBezier2cp(start,cp,cp2,end)

    for i in range(iterationNum):
        print('step:',i,' of ',iterationNum)
        bInst.step(granulate,interpolateGranules)

    bInst.draw(interpolate,interpolateGrains)
