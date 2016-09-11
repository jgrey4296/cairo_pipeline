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
from branches import Branches
from voronoi import Voronoi

#constants:
PIX = 1/pow(2,10)
op = None
drawInstance = None
branchInstance = None
voronoiInstance = None
numOfElements = 10
iterationNum = 10
granulate = True
interpolateGranules = False
interpolate = True
interpolateGrains = False

branchIterations = 100

voronoi_nodes = 30


#top level draw command:
def draw(ctx, drawOption,X_size,Y_size):
    print("Drawing: ",drawOption)
    global op
    global drawInstance
    global branchInstance
    global voronoiInstance
    op = ctx.get_operator()
    #setup the draw instances
    drawInstance = SandSpline(ctx,(X_size,Y_size))
    branchInstance = Branches(ctx,(X_size,Y_size))
    voronoiInstance = Voronoi(ctx,(X_size,Y_size),voronoi_nodes)
    #ctx.set_operator(OPERATOR_SOURCE)
    utils.clear_canvas(ctx)

    #Initialise the base image:
    if drawOption == 'circles':
        initCircles()
        iterateAndDraw()
    elif drawOption == "lines":
        initLines()
        iterateAndDraw()
    elif drawOption == "singleLine":
        initSpecificLine()
        iterateAndDraw()
    elif drawOption == "bezier":
        bezierTest()
        iterateAndDraw()
    elif drawOption == "manycircles":
        manyCircles()
        iterateAndDraw()
    elif drawOption == "branch":
        drawBranch(X_size,Y_size)
    elif drawOption == "voronoi":
        drawVoronoi(X_size,Y_size)
    else:
        raise Exception("Unrecognized draw routine",drawOption)

#step the drawing deformation:
def iterateAndDraw():
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
    
def drawBranch(X_size,Y_size):
    branchInstance.addBranch()
    for i in np.arange(branchIterations):
        print('Branch Growth:',i)
        branchInstance.grow(i)
    branchInstance.draw()

def drawVoronoi(X_size,Y_size):
    voronoiInstance.initGraph()
    voronoiInstance.calculate()
    voronoiInstance.draw()
