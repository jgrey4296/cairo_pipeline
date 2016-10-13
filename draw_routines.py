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
import utils
import logging
from random import choice
#Drawing classes
from ssClass import SandSpline
from branches import Branches
from voronoi import Voronoi
from voronoiexperiments import VExperiment

#constants:
DRAW_INTERMEDIATE = False
PIX = 1/pow(2,10)
op = None
cairo_surface = None
filename = None
#instances of drawing classes
drawInstance = None
branchInstance = None
voronoiInstance = None
vexpInstance = None

numOfElements = 10
iterationNum = 10
granulate = True
interpolateGranules = False
interpolate = True
interpolateGrains = False

branchIterations = 100

voronoi_nodes = 10


#top level draw command:
def draw(ctx, drawOption,X_size,Y_size,surface=None,filenamebase="cairo_render"):
    """ The generic setup function main calls for all drawing """
    logging.info("Drawing: {}".format(drawOption))
    #modify and update globals:
    global op
    global drawInstance
    global branchInstance
    global voronoiInstance
    global vexpInstance
    global cairo_surface
    global filename
    cairo_surface = surface
    filename = filenamebase
    op = ctx.get_operator()
    #setup the draw instances
    drawInstance = SandSpline(ctx,(X_size,Y_size))
    branchInstance = Branches(ctx,(X_size,Y_size))
    voronoiInstance = Voronoi(ctx,(X_size,Y_size),voronoi_nodes)
    vexpInstance = VExperiment(ctx,(X_size,Y_size),voronoi_nodes)
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
    elif drawOption == "vexp":
        drawVExp(X_size,Y_size)
    else:
        raise Exception("Unrecognized draw routine",drawOption)

    if surface:
        utils.write_to_png(surface,filenamebase)
    
def iterateAndDraw():
    """ Run transforms repeatedly on non-voronoi drawing classes """
    for i in range(iterationNum):
        logging.info('step:',i)
        drawInstance.step(granulate,interpolateGranules)
    
    drawInstance.draw(interpolate,interpolateGrains)
#------------------------------

def initCircles():
    """ Add a number of circles to the drawing instance, ready for deformation """
    for i in range(numOfElements):
        logging.info('adding circle:',i)
        drawInstance.addCircle()

def initLines():
    """ Add a number of lines to the drawing instance, ready for deformation """
    for i in range(numOfElements):
        logging.info('adding line:',i)
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
        logging.info('Branch Growth:',i)
        branchInstance.grow(i)
    branchInstance.draw()

#----------
# VORONOI:
#----------
def drawVoronoi(X_size,Y_size):
    """ Step through the construction of a voronoi diagram """
    i = 0
    result = True
    siteLocations = None
    loaded = False
    try: #try to load a saved set of points
        siteLocations = voronoiInstance.load_graph()
        loaded = True
    except Exception as e:
        logging.warn("Using Default Locations")
    #setup the points internally
    siteLocations = voronoiInstance.initGraph(data=siteLocations)
    #Save the points for reuse
    if not loaded:
        voronoiInstance.save_graph(siteLocations)
        
    #Draw the starting set of points    
    voronoiInstance.draw_intermediate_states()
    utils.write_to_png(cairo_surface,filename,i)
    
    while result:
        i += 1
        logging.info("\n---------- Calculating step {}".format(i))
        logging.info(voronoiInstance.beachline)
        
        #The main algorithm step:
        result = voronoiInstance.calculate(i)
        
        logging.info("----- Beachline Modifications:")
        logging.info(voronoiInstance.beachline)
        logging.info("----")

        #Debug intermediate images:
        if DRAW_INTERMEDIATE:
            voronoiInstance.draw_intermediate_states()
            voronoiInstance.draw_voronoi_diagram(clear=False)
            utils.write_to_png(cairo_surface,filename,i)

        #rough infinite loop guard
        if i > 150:
            raise Exception('Voronoi has run too long')

    logging.info("-------------------- Finalising")
    #calculations finished, get the final DCEL:
    dcel = voronoiInstance.finalise_DCEL(surface=cairo_surface,filename=filename)

    #Draw each face individually
    for i,f in enumerate(dcel.faces):
        logging.info("Drawing face: {}".format(i))
        faceName = "{}_face_{}".format(filename,i)
        utils.draw_dcel_single_face(voronoiInstance.ctx,dcel,f)
        utils.write_to_png(cairo_surface,faceName)
    
    voronoiInstance.draw_voronoi_diagram()
    finalFilename = "{}-FINAL".format(filename)
    utils.write_to_png(cairo_surface,finalFilename,i+1)

def drawVExp(X_size,Y_size):
    vexpInstance.drawTest()
    

def example_multi_render(Xs,Ys):
    for i in range(1000):
        #do something
        if i%10:
            utils.write_to_png(surface,filename,i=i)
