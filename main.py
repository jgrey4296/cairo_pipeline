#!/users/jgrey/anaconda/bin/python
import sys
import time
import math
import cairo
import logging

import cairo_utils as utils
#constants
N = 12
imgPath = "./imgs/"
imgName = "initialTest"
currentTime = time.gmtime()
FONT_SIZE = 0.03
#format the name of the image to be saved thusly:
saveString = "{}{}_{}-{}_{}-{}".format(imgPath,
                                       imgName,
                                       currentTime.tm_min,
                                       currentTime.tm_hour,
                                       currentTime.tm_mday,
                                       currentTime.tm_mon,
                                       currentTime.tm_year)


#get the type of drawing to do from the command line argument:
if len(sys.argv) > 1:
    drawRoutineName = sys.argv[1]
else:
    drawRoutineName = "circles"

#setup logging:
LOGLEVEL = logging.DEBUG
logFileName = "log.{}".format(drawRoutineName)
logging.basicConfig(filename=logFileName,level=LOGLEVEL,filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

#setup
surface, ctx, size, n = utils.drawing.setup_cairo(n=N)

#Drawing:
