"""
A Drawing class based on inconvergents sandsplines
"""
import numpy as np
from numpy.random import random
import cairo_utils as utils
import IPython
from .pdraw import PDraw
from . import constants
import IPython

def SandPipeline(d, opts, data):
    """ Treats data as sequences to be displaced by noisy sine signals """
    n = data['n']
    easing = utils.easings.lookup(opts['easing'])
    easing_2 = utils.easings.lookup('pow_cos_pi')
    ramp = easing(np.linspace(0,1,n), 0)
    ramp2 = easing_2(np.linspace(-1,1,n), 3.5)

    scale = opts['scale']
    samples = d._samples[1:].reshape((-1, n, constants.SAMPLE_DATA_LEN))
    result = np.zeros((1,constants.SAMPLE_DATA_LEN))

    for sample_set in samples:
        xys = sample_set[:,:2]
        rst = sample_set[:,2:].repeat(opts['channels'], axis=0)

        # base random signal
        # TODO: make this a separate layer? make it FM or AM or additive?
        noise = easing((1.0-2.0 * random((opts['channels'], 1, 1))), 0)
        rads = (ramp * opts['speed']) * ramp2 * utils.umath.TWOPI * noise
        rotation = np.column_stack((-np.cos(opts['phase'] + rads), np.sin(opts['phase'] + rads)))
        combined = rotation * scale * noise

        formatted = combined.reshape((opts['channels'], n, 2), order='F')

        i_xys = (xys + formatted).reshape((-1,2))
        recombined = np.column_stack((i_xys, rst))

        #recombine
        result = np.row_stack((result, recombined))

    d._samples = np.row_stack((d._samples, result[1:]))
    return data

def granulate_layer(d, opts, data):
    currentGrains = utils.math.granulate(points, grains=grains, mult=grainMult)
    #points = utils.math._interpolate(points, sampleSize, smoothing=d.smooth)
    if interpolateGrains:
        currentGrains = utils.math._interpolate(currentGrains, d.interpolationPoints, smoothing=d.smooth)
        d.calculatedGrains.append(currentGrains)

    return data
