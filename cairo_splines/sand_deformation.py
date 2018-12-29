"""
A Drawing class based on inconvergents sandsplines
"""
import numpy as np
from numpy.random import random
import cairo_utils as utils
import IPython
from simple_draw import SimpleDraw

def SandDraw(d, i, frontier=None):

    #process each 'set' of xy points, with its associated column of noise
    for sampleSize, xyList, noise in zip(d.snums, d.xys, d.noise):
        r = (1.0-2.0 * random((sampleSize, 1))) * rMod
        scale = np.arange(sampleSize).astype('float').reshape((sampleSize, 1))
        #increment the noise
        noise[:] += r * scale * d.noise_stp

        #create rotation points
        a = random(sampleSize)*TWOPI
        rnd = np.column_stack((np.cos(a), np.sin(a)))

        #get the points and modify by the noise amount
        points = xyList[:, :]
        points += rnd * d.recRes * noise

        #if necessary granulate
        if granulate:
            currentGrains = utils.math.granulate(points, grains=grains, mult=grainMult)
            #points = utils.math._interpolate(points, sampleSize, smoothing=d.smooth)
            if interpolateGrains:
                currentGrains = utils.math._interpolate(currentGrains, d.interpolationPoints, smoothing=d.smooth)
            d.calculatedGrains.append(currentGrains)

        #copy the points back into the main data store
        xyList[:, :] = points
        #add in the varied points after interpolating
        d.i_xys.append(utils.math._interpolate(xyList, d.interpolationPoints, smoothing=d.smooth))
