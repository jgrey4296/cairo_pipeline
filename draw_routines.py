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

#Drawing classes
from ssClass import SandSpline

#constants:
PIX = 1/pow(2,10)
op = None
drawInstance = None
numOfElements = 10
iterationNum = 10
granulate = True
interpolateGranules = False
interpolate = True
interpolateGrains = False

#top level draw command:
def draw(ctx, drawOption,X_size,Y_size):
    print("Drawing: ",drawOption)
    global op
    global drawInstance
    op = ctx.get_operator()
    drawInstance = SandSpline(ctx,(X_size,Y_size))
    #ctx.set_operator(OPERATOR_SOURCE)
    utils.clear_canvas(ctx)

    #Initialise the base image:
    if drawOption == 'circles':
        initCircles()
    elif drawOption == "lines":
        initLines()
    elif drawOption == "singleLine":
        initSpecificLine()
    elif drawOption == "bezier":
        bezierTest()
    elif drawOption == "manycircles":
        manyCircles()
    else:
        raise Exception("Unrecognized draw routine",drawOption)

    #step the drawing deformation:
    for i in range(iterationNum):
        print('step:',i)
        drawInstance.step(granulate,interpolateGranules)
    
    drawInstance.draw(interpolate,interpolateGrains)
#------------------------------

def initCircles():
    for i in range(numOfElements):
        print('adding circle:',i)
        drawInstance.addCircle()

def initLines():
    for i in range(numOfElements):
        print('adding line:',i)
        line = [x for x in random(4)]
        drawInstance.addLine(*line)

def initSpecificLine():
    drawInstance.addLine(0.1,0.5,0.9,0.5)

def bezierTest():
    start = [0.0,0.5]
    cp = [0.4,0.6]
    cp2 = [0.8,0.1]
    end = [1.0,0.5]
    drawInstance.addBezier2cp(start,cp,cp2,end)

def manyCircles():
    xs = np.linspace(0.1,0.9,10)
    ys = np.linspace(0.1,0.9,10)

    for x in xs:
        for y in ys:
            drawInstance.addCircle(x,y,0.0002,0.0003)
    
