from ssClass import SandSpline
import utils
import numpy as np
from numpy.random import random
import IPython

class LineSpline(SandSpline):

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
        
                                        


