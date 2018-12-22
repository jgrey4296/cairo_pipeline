"""
A Drawing class based on inconvergents sandsplines
"""
import numpy as np
from numpy.random import random
import cairo_utils as utils
import IPython
from simple_draw import SimpleDraw

#replicating inconvergents sand spline
class SandSpline(SimpleDraw):

    def __init__(self, ctx, sizeTuple):
        super().__init__(self, ctx, sizeTuple)

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
    def draw(self, interpolate, interpolateGrains):
        return


    #------------------------------
    def iterate(self, frontier=None):
        #track the amount of steps processed:
        self.itt += 1

        #process each 'set' of xy points, with its associated column of noise
        for sampleSize, xyList, noise in zip(self.snums, self.xys, self.noise):
            r = (1.0-2.0 * random((sampleSize, 1))) * rMod
            scale = np.reshape(np.arange(sampleSize).astype('float'), (sampleSize, 1))
            #increment the noise
            noise[:] += r * scale * self.noise_stp

            #create rotation points
            a = random(sampleSize)*TWOPI
            rnd = np.column_stack((np.cos(a), np.sin(a)))

            #get the points and modify by the noise amount
            points = xyList[:, :]
            points += rnd * self.recRes * noise

            #if necessary granulate
            if granulate:
                currentGrains = utils.math.granulate(points, grains=grains, mult=grainMult)
                #points = utils.math._interpolate(points, sampleSize, smoothing=self.smooth)
                if interpolateGrains:
                    currentGrains = utils.math._interpolate(currentGrains, self.interpolationPoints, smoothing=self.smooth)
                self.calculatedGrains.append(currentGrains)

            #copy the points back into the main data store
            xyList[:, :] = points
            #add in the varied points after interpolating
            self.i_xys.append(utils.math._interpolate(xyList, self.interpolationPoints, smoothing=self.smooth))
