import math
import cairo
from cairo import OPERATOR_SOURCE
import numpy as np
from numpy import pi, linspace, cos, sin
from numpy.random import random
from scipy.interpolate import splprep, splev
import cairo_utils as utils
import IPython
import logging
from random import choice
#Drawing classes
from ssClass import SandSpline
from branches import Branches
from GraphLines import GraphLines

#Globals and constants:
PIX = 1/pow(2,10)
op = None
cairo_surface = None
cairo_context = None
filename = None
numOfElements = 10
iterationNum = 10
branchIterations = 100

#Processing types:
granulate = True
interpolateGranules = False
interpolate = True
interpolateGrains = True

#instances of drawing classes
drawInstance = None
branchInstance = None



#top level draw command:
def draw(ctx, drawOption,X_size,Y_size,surface=None,filenamebase="cairo_render"):
    """ The generic setup function main calls for all drawing """
    logging.info("Drawing: {}".format(drawOption))
    #modify and update globals:
    global op
    global drawInstance
    global branchInstance
    global cairo_surface
    global cairo_context
    global filename
    cairo_surface = surface
    cairo_context = ctx
    filename = filenamebase
    op = ctx.get_operator()
    #setup the draw instances
    drawInstance = SandSpline(ctx,(X_size,Y_size))
    branchInstance = Branches(ctx,(X_size,Y_size))
    #ctx.set_operator(OPERATOR_SOURCE)
    utils.drawing.clear_canvas(ctx)

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
    elif drawOption == "textTest":
        drawTextTest(X_size,Y_size)
    elif drawOption == "graphLines":
        graphL = GraphLines(ctx, (X_size, Y_size), numPoints=10, numLayers=4)
        graphL.draw()
        
    else:
        raise Exception("Unrecognized draw routine",drawOption)

    if surface:
        utils.drawing.write_to_png(surface,filenamebase)
    
def iterateAndDraw():
    """ Run transforms repeatedly on drawing classes """
    for i in range(iterationNum):
        logging.info('step: {}'.format(i))
        drawInstance.step(granulate,interpolateGranules)
    
    drawInstance.draw(interpolate,interpolateGrains)
#------------------------------

def initCircles():
    """ Add a number of circles to the drawing instance, ready for deformation """
    for i in range(numOfElements):
        logging.info('adding circle: {}'.format(i))
        drawInstance.addCircle()

def initLines():
    """ Add a number of lines to the drawing instance, ready for deformation """
    for i in range(numOfElements):
        logging.info('adding line:'.format(i))
        line = [x for x in random(4)]
        drawInstance.addLine(*line)

def initSpecificLine():
    """ Add just a single line  """
    drawInstance.addLine(0.1,0.5,0.9,0.5)

def bezierTest():
    """ Setup a simple bezier curve for deformation  """
    start = [0.0,0.5]
    cp = [0.4,0.6]
    cp2 = [0.8,0.1]
    end = [1.0,0.5]
    drawInstance.addBezier2cp(start,cp,cp2,end)

def manyCircles():
    """ Add a number of circles for deformation """
    xs = np.linspace(0.1,0.9,10)
    ys = np.linspace(0.1,0.9,10)

    for x in xs:
        for y in ys:
            drawInstance.addCircle(x,y,0.0002,0.0003)
    
def drawBranch(X_size,Y_size):
    """ Incomplete, intended to draw trees  """
    branchInstance.addBranch()
    for i in np.arange(branchIterations):
        logging.info('Branch Growth: {}'.format(i))
        branchInstance.grow(i)
    branchInstance.draw()

def drawTextTest(x,y):
    cairo_context.set_font_size(0.025)
    cairo_context.set_source_rgba(*[0,1,1,1])
    cairo_context.move_to(0.2,0.5)
    cairo_context.show_text("hello")
    utils.drawing.write_to_png(cairo_surface,"text_test")                  

    
def example_multi_render(Xs,Ys):
    for i in range(1000):
        #do something
        if i%10:
            utils.drawing.write_to_png(surface,filename,i=i)

            
