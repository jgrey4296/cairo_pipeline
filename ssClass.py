import numpy as np
from numpy.random import random
import utils
import IPython

TWOPI = np.pi*2
HPI = np.pi * 0.5
sampleRange = [10,200]
radiusRange = [0.2,0.25]
interpolationPoints = 3000
p_r = 0.0005 #an individual point radius
noiseAmnt = 0.1
grains = 20
grainMult = 1.3
smooth = 0.00
ALPHA = 0.05
rMod = 1

#replicating inconvergents sand spline
class SandSpline(object):

    def __init__(self,ctx,sizeTuple):
        self.ctx = ctx
        self.sX = sizeTuple[0]
        self.sY = sizeTuple[1]

        self.interpolationPoints = interpolationPoints
        self.sampleRange = sampleRange
        self.smooth = smooth
        
        #interation counter:
        self.itt = 0
        #resolution:
        self.resolution = sizeTuple[0]
        #reciprocal resolution:
        self.recRes = 1.0 / sizeTuple[0]
        #noise variance
        self.noise_stp = noiseAmnt
        #tracker of raw xy points:
        self.xys = []
        #tracker of output interpolated points:
        self.i_xys = []
        #tracker of noise points:
        self.noise = []
        #tracker of sample amounts:
        self.snums = []
        #calculated grains:
        self.calculatedGrains = []
        
    #------------------------------
    # SHAPES
    #------------------------------

    def addLine(self,x,y,x2,y2):
        sampleSize = (self.sampleRange[0] + (random(1) * self.sampleRange[1])).astype('int')[0]
        lineX = sorted(x + (random(sampleSize) * (x2 - x)))
        lineY = sorted(y + (random(sampleSize) * (y2 - y)))
        line = np.column_stack((lineX,lineY))
        i2_line = utils._interpolate(line,self.interpolationPoints,smoothing=self.smooth)
        initialNoise = np.zeros((sampleSize,1),'float')
        self.snums.append(sampleSize)
        self.xys.append(line)
        self.i_xys.append(i2_line)
        self.noise.append(initialNoise)

    def addBezier(self,start,cp1,end):
        sampleSize = (self.sampleRange[0] + (random(1) * self.sampleRange[1])).astype('int')[0]

        line = utils.bezier1cp(*start,*cp1,*end,sampleSize)
        i2_line = utils._interpolate(line,self.interpolationPoints,smoothing=self.smooth)
        initialNoise = np.zeros((sampleSize,1),'float')
        self.snums.append(sampleSize)
        self.xys.append(line)
        self.i_xys.append(i2_line)
        self.noise.append(initialNoise)

    def addBezier2cp(self,start,cp1,cp2,end):
        sampleSize = (self.sampleRange[0] + (random(1) * self.sampleRange[1])).astype('int')[0]

        line = utils.bezier2cp(start,cp1,cp2,end,sampleSize)
        i2_line = utils._interpolate(line,self.interpolationPoints,smoothing=self.smooth)
        initialNoise = np.zeros((sampleSize,1),'float')
        self.snums.append(sampleSize)
        self.xys.append(line)
        self.i_xys.append(i2_line)
        self.noise.append(initialNoise)

    
    def addCircle(self,x=0.5,y=0.5,rLower=radiusRange[0],rHigher=radiusRange[1]):
        sampleSize = (self.sampleRange[0] + (random(1) * self.sampleRange[1])).astype('int')[0]
        randPoints = sorted(random(sampleSize)*TWOPI)

        xPoints = x + np.cos(randPoints) * (rLower + random(1) * rHigher)
        yPoints = y + np.sin(randPoints) * (rLower + random(1) * rHigher)
        
        circlePoints = np.column_stack((xPoints,yPoints))

        #IPython.embed()
        interpolatedPoints = utils._interpolate(circlePoints,self.interpolationPoints,smoothing=self.smooth)

        initialNoise = np.zeros((sampleSize,1),'float')

        #store the generated info:
        self.snums.append(sampleSize)
        self.xys.append(circlePoints)
        self.i_xys.append(interpolatedPoints)
        self.noise.append(initialNoise)

    #------------------------------
    def draw(self,interpolate,interpolateGrains):
        print('drawing')
        lxys = len(self.i_xys)
        lgrains = len(self.calculatedGrains)
        for i,xy in enumerate(self.i_xys):
            color = [x for x in np.random.random(3)]
            self.ctx.set_source_rgba(*color,ALPHA)
            points = xy
            
            if interpolate:
                print('interpolating',i,' of ', lxys)
                points = utils._interpolate(points,self.interpolationPoints, smoothing=self.smooth)
                        
            for x,y in points:
                utils.drawCircle(self.ctx,x,y,p_r)

        for i,xy in enumerate(self.calculatedGrains):
            color = [x for x in np.random.random(3)]
            self.ctx.set_source_rgba(*color,ALPHA)

            points = xy
            if interpolateGrains:
                print('interpolating grains',i,' of ',lgrains)
                for x,y in points:
                    utils.drawCircle(self.ctx,x,y,p_r)
            

    #------------------------------
    def step(self,granulate,interpolateGrains):
        self.itt += 1
        
        for sampleSize,xyList,noise in zip(self.snums,self.xys,self.noise):
            r = (1.0-2.0 * random((sampleSize,1))) * rMod
            scale = np.reshape(np.arange(sampleSize).astype('float'),(sampleSize,1))
            noise[:] += r * scale * self.noise_stp

            a = random(sampleSize)*TWOPI
            rnd = np.column_stack((np.cos(a),np.sin(a)))

            points = xyList[:,:]
            points += rnd * self.recRes * noise
            
            if granulate:
                currentGrains = utils.granulate(points,grains=grains,mult=grainMult)
                #points = utils._interpolate(points,sampleSize,smoothing=self.smooth)
                if interpolateGrains:
                    currentGrains = utils._interpolate(currentGrains,self.interpolationPoints, smoothing=self.smooth)
                self.calculatedGrains.append(currentGrains)
                

            xyList[:,:] = points
            self.i_xys.append(utils._interpolate(xyList,self.interpolationPoints,smoothing=self.smooth))

            
        
