#!/users/jgrey/anaconda/bin/python

import time
import math
import cairo
import first

#constants
N = 12
X = pow(2,N)
Y = pow(2,N)
imgPath = "./imgs/"
imgName = "initialTest"
currentTime = time.gmtime()
saveString = "%s%s_%s-%s-%s_%s-%s.png" % (imgPath,
                                          imgName,
                                          currentTime.tm_min,
                                          currentTime.tm_hour,
                                          currentTime.tm_mday,
                                          currentTime.tm_mon,
                                          currentTime.tm_year)
    
#setup
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, X,Y)
ctx = cairo.Context(surface)
ctx.scale(X,Y)
    
#Drawing:
first.draw(ctx)
    
#write to file:
print('Saving')
surface.write_to_png (saveString)

