import numpy as np
import cairo_utils as utils

def ColourPipeline(d, pipeline_data):
    """ Create a gentle variation of colours """

    easing = utils.easings.lookup("sigmoid")

    samples = d._samples
    non_colour = samples[:,:-4]
    colours = samples[:,-4:]

    c_i = (np.arange(len(colours)) / len(colours)).reshape((len(colours), 1))
    rnd = np.random.random((colours.shape))
    cos_c = np.cos((50 * c_i) * (rnd * 25))

    col_prime = colours * cos_c

    sig_col = easing(col_prime, 0)#, codomain_e=utils.easings.CODOMAIN.RIGHT)

    col_prime2 = utils.easings.quantize(sig_col)
    d._samples = np.hstack((non_colour, col_prime2))
    return pipeline_data
