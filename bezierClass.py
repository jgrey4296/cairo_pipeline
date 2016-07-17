from ssClass import SandSpline
import utils
import numpy as np
from numpy.random import random
import IPython

class BezierLine(SandSpline):

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
