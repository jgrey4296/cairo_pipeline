#!/Users/jgrey/anaconda/bin/python
import cairo
import logging
import math
import numpy as np
import sys
import time
import cairo_utils as utils
import cairo_pipeline as cp

#constants
N = 12
imgPath = "./imgs/"

#setup logging:
LOGLEVEL = logging.DEBUG
logFileName = "log.{}".format("pipeline")
logging.basicConfig(filename=logFileName,level=LOGLEVEL,filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

#setup
surface, ctx, size, n = utils.drawing.setup_cairo(n=N,
                                                  scale=False,
                                                  cartesian=True)

#Drawing:
# create the drawing object
d_o = cp.PDraw(ctx, (size, size), surface, imgPath)
# Run a selected pipeline:
d_o.pipeline(cp.pipelines.heightmap.heightmap_p)
