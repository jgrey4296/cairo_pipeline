#!/users/jgrey/anaconda/bin/python

import time
import math
import cairo
import first

#constants
N = pow(2,12)
imgPath = "./imgs/"
imgName = "initialTest"
currentTime = time.gmtime()
saveString = "%s%s_%s-%s-%s_%s-%s.png" % (imgPath, imgName, currentTime.tm_min, currentTime.tm_hour, currentTime.tm_mday, currentTime.tm_mon, currentTime.tm_year)
    
#setup
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, N,N)
ctx = cairo.Context(surface)
ctx.scale(N,N)
    
#Drawing:
first.draw(ctx,N,N)
    
#write to file:
surface.write_to_png (saveString)

