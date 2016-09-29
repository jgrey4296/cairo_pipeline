import numpy as np
import IPython

from Quadratic import Quadratic as Q

class Parabola(object):
    #todo: if fy-d == 0: degenerate case, is a straight line
    #todo: let calculate take a current d line

    def __init__(self,fx,fy,d):
        """ Create a parabola with a focus x and y, and a directrix y """
        #breakout for degenerate case
        self.vertical_line = False
        self.fx = fx
        self.fy = fy
        self.d = d
        #focal parameter: the distance from vertex to focus/directrix
        self.p = 0.5 * (self.fy - self.d)
        #Vertex form: y = a(x-h)^2 + k
        if self.fy - self.d == 0:
            self.va = 0
            self.vertical_line = True
        else:
            self.va = 1/(2*(self.fy-self.d))
            self.vertical_line = False
        self.vh = -self.fx
        self.vk = self.fy - self.p
        #standard form: y = ax^2 + bx + c
        self.sa = self.va
        self.sb = 2 * self.sa * self.vh
        self.sc = self.sa * (pow(self.vh,2)) + self.vk

    def __str__(self):
        return "y = {0:.2f} * x^2 + {1:.2f} x + {2:.2f}".format(self.sa,self.sb,self.sc)
        
    def is_left_of_focus(self,x):
        return x < self.fx
        
    def update_d(self,d):
        """ Update the parabola given the directrix has moved """
        self.d = d
        self.p = 0.5 * (self.fy - self.d)
        #Vertex form parameters:
        if self.fy-self.d == 0:
            self.va = 0
            self.vertical_line = True
        else:
            self.va = 1/(2*(self.fy-self.d))
            self.vertical_line = False
        self.vk = self.fy - self.p
        #standard form:
        self.sa = self.va
        self.sb = 2 * self.sa * self.vh
        self.sc = self.sa * (pow(self.vh,2)) + self.vk
        
    def intersect(self,p2,d=None):
        """ Take the quadratic representations of parabolas, and
            get the 0, 1 or 2 points that are the intersections
        """
        if d:
            self.update_d(d)
            p2.update_d(d)
        q1 = Q(self.sa,self.sb,self.sc)
        q2 = Q(p2.sa,p2.sb,p2.sc)
        xs = q1.intersect(q2)
        xys = self(xs)
        return xys
        
        
    def toStandardForm(self,a,h,k):
        """ Calculate the standard form of the parabola from a vertex form """
        return [
            a,
            -2*a*h,
            a*pow(h,2)+k
        ]

    def toVertexForm(self,a,b,c):
        """ Calculate the vertex form of the parabola from a standard form """
        return [
            a,
            -b/(2*a),
            c-(a * (pow(b,2) / 4 * a))
        ]
    
    def calcStandardForm(self,x):
        """ Get the y value of the parabola at an x position using the standard
            form equation. Should equal calcVertexForm(x)
        """
        return self.sa * pow(x,2) + self.sb * x + self.sc

    def calcVertexForm(self,x):
        """ Get the y value of the parabola at an x position using 
            the vertex form equation. Should equal calcStandardForm(x)
        """
        return self.va * pow(x + self.vh,2) + self.vk
    
    def calc(self,x):
        """ For given xs, return an (n,2) array of xy pairs of the parabola """
        return np.column_stack((x,self.calcVertexForm(x)))
    
    def __call__(self,x):
        if self.vertical_line:
            ys = np.linspace(0,self.fy,1000)
            xs = np.repeat(self.fx,1000)
            return np.column_stack((xs,ys))            
        else:
            return np.column_stack((x,self.calcStandardForm(x)))

    def __eq__(self,parabola2):
        if self.fx == parabola2.fx \
           and self.fy == parabola2.fy \
           and self.va == parabola2.va \
           and self.vh == parabola2.vh \
           and self.vk == parabola2.vk \
           and self.sa == parabola2.sa \
           and self.sb == parabola2.sb \
           and self.sc == parabola2.sc:
            return True
        else:
            return False

    def get_focus(self):
        return np.array([[self.fx,self.fy]])
