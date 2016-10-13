import IPython
from math import atan2,sqrt
import logging
import utils
import numpy as np

# An implementation of a Double-Edge Connected List
# from de Berg's Computational Geometry Book
# Intended for use with cairo

class Vertex:
    """ A Simple vertex for two dimension """
    
    def __init__(self,x,y,iEdge=None):
        logging.debug("Creating vertex at: {} {}".format(x,y))
        self.x = x
        self.y = y
        self.incidentEdge = iEdge
        self.halfEdges = []

    def registerHalfEdge(self,he):
        self.halfEdges.append(he)

    def within(self,bbox):
        """ Check the vertex is within [x,y,x2,y2] """
        inXBounds = bbox[0] <= self.x and self.x <= bbox[2]
        inYBounds = bbox[1] <= self.y and self.y <= bbox[3]
        return inXBounds and inYBounds
        
    def outside(self,bbox):
        """ Check the vertex is entirely outside of the bbox [x,y,x2,y2] """
        inXBounds = bbox[0] <= self.x and self.x <= bbox[2]
        inYBounds = bbox[1] <= self.y and self.y <= bbox[3]
        return not inXBounds and not inYBounds
    
class Line:
    """ A line as a start x and y, a direction, and a length """
    
    def __init__(self,sx,sy,dx,dy,l):
        self.source = np.array([sx,sy])
        self.direction = np.array([dx,dy])
        self.length = l

    def constrain(self,min_x,min_y,max_x,max_y):
        """ Intersect the line with a bounding box, adjusting points as necessary """
        #min and max: [x,y]
        dest = self.destination()
        npArray_line = np.column_stack((self.source,dest))
        bbox_lines = [np.array([min_x,min_y,max_x,min_y]),
                      np.array([min_x,max_y,max_x,max_y]),
                      np.array([min_x,min_y,min_x,max_y]),
                      np.array([max_x,min_y,max_x,max_y])]
        #intersect one of the bbox lines
        p = None
        while p is None and len(bbox_lines) > 0:
            p = utils.intersect(npArray_line,bbox_lines.pop())
        if p is not None:
            new_length = sqrt(pow(p[0]-self.source[0],2) + pow(p[1]-self.source[1],2))
            if new_length != 0:
                self.length = new_length
        
    def destination(self):
        """ Calculate the destination vector of the line """
        ex = self.source[0] + (self.length * self.direction[0])
        ey = self.source[1] + (self.length * self.direction[1])
        return np.array([ex,ey])

    def bounds(self):
        return np.row_stack((self.source,self.destination()))
    
    @staticmethod
    def newLine(a,b):
        """ Create a new line from two vertices """
        #todo: detect which point is closer to the centre of the bounding box,
        #and use that as the start point
        vx = b.x - a.x
        vy = b.y - a.y
        l = sqrt(pow(vx,2) + pow(vy,2))
        if l != 0:
            scale = 1/l
        else:
            scale = 0
        dx = vx * scale
        dy = vy * scale
        cx = a.x + (dx * l)
        cy = a.y + (dy * l)
        return Line(a.x,a.y,dx,dy,l)
    
        
        
#--------------------
class HalfEdge:
    """ A Canonical Half-Edge. Has an origin point, and a twin half-edge for its end point """
    
    def __init__(self, origin, twin=None):
        self.origin = origin
        if origin:
            self.origin.registerHalfEdge(self)
        self.twin = twin
        self.face = None
        self.next = None
        self.prev = None

        #Additional:
        self.sourceNode = None
        self.successorNode = None
        self.markedForCleanup = False
        

    def constrain(self,bbox):
        """ Constrain the half-edge to be with a bounding box of [min_x,min_y,max_x,max_y]"""
        if self.twin is None: 
            raise Exeption("Can't bound a single half-edge")
        if self.twin.origin is None:
            raise Exception("By this stage all edges should be finite")
        if self.origin is None:
            raise Exception("By this stage all edges should have an origin")

        #Convert to an actual line representation, for intersection 
        asLine = Line.newLine(self.origin,self.twin.origin)
        asLine.constrain(*bbox)
        return asLine.bounds()
        
        
    def addVertex(self,vertex):
        if self.origin is None:
            self.origin = vertex
            self.origin.registerHalfEdge(self)
        elif self.twin.origin is None:
            self.twin.origin = vertex
            self.twin.origin.registerHalfEdge(self)
            
        if self.origin is not None and self.twin.origin is not None:
            #now switch if necessary to maintain counter-clockwise-ness?
            angle = utils.angle_between_points([self.origin.x,self.origin.y],
                                               [self.twin.origin.x,self.twin.origin.y])
            if angle < 0: #is clockwise, so flip
                self.twin.origin.halfEdges.remove(self.twin)
                self.origin.halfEdges.remove(self)
                temp = self.twin.origin
                self.twin.origin = self.origin
                self.twin.origin.registerHalfEdge(self.twin)
                self.origin = temp
                self.origin.registerHalfEdge(self)

            
    def swapFaces(self):
        if not self.face and self.twin.face:
            raise Exception("Can't swap faces when at least one is missing")
        oldFace = self.face
        self.face = self.twin.face
        self.twin.face = oldFace
        
    def setNext(self,nextEdge):
        self.next = nextEdge
        
    def setPrev(self,prevEdge):
        self.prev = prevEdge
        
    def getVertices(self):
        return (self.origin,self.twin.origin)

    def isInfinite(self):
        return self.origin is None or self.twin is None or self.twin.origin is None
    
#--------------------
class Face(object):
    """ A Face with a start point for its outer component list, and all of its inner components """
    
    def __init__(self):
        #Starting point for bounding edges, going anti-clockwise
        self.outerComponent = None
        #Clockwise inner loops
        self.innerComponents = []
        self.unsortedEdges = []
        
#--------------------
class DCEL(object):
    """ The total DCEL data structure, stores vertices, edges, and faces """
    
    def __init__(self):
        self.vertices  = []
        self.faces     = []
        self.halfEdges = []

    def __str__(self):
        verticesDescription = "Vertices: num: {}".format(len(self.vertices))
        edgesDescription = "HalfEdges: num: {}".format(len(self.halfEdges))
        facesDescription = "Faces: num: {}".format(len(self.faces))

        allVertices = [x.getVertices() for x in self.halfEdges]
        flattenedVertices = [x for (x,y) in allVertices for x in (x,y)]
        setOfVertices = set(flattenedVertices)
        vertexSet = "Vertex Set: num: {}/{}".format(len(setOfVertices),len(flattenedVertices))

        infiniteEdges = [x for x in self.halfEdges if x.isInfinite()]
        infiniteEdgeDescription = "Infinite Edges: num: {}".format(len(infiniteEdges))

        completeEdges = []
        for x in self.halfEdges:
            if not x in completeEdges and x.twin not in completeEdges:
                completeEdges.append(x)

        completeEdgeDescription = "Complete Edges: num: {}".format(len(completeEdges))

        edgelessVertices = [x for x in self.vertices if len(x.halfEdges) == 0]
        edgelessVerticesDescription = "Edgeless vertices: num: {}".format(len(edgelessVertices))

        edgeCountForFaces = [str(len(f.innerComponents)) for f in self.faces]
        edgeCountForFacesDescription = "Edge Counts for Faces: {}".format("-".join(edgeCountForFaces))
        
        return "\n".join(["---- DCEL Description: ",verticesDescription,edgesDescription,facesDescription,vertexSet,infiniteEdgeDescription,completeEdgeDescription,edgelessVerticesDescription,edgeCountForFacesDescription,"----\n"])
        
    def newVertex(self,x,y):
        """ Get a new vertex """
        newVertex = Vertex(x,y)
        self.vertices.append(newVertex)
        return newVertex
    
    def newEdge(self,originVertex,twinVertex,face=None,twinFace=None,prev=None,prev2=None):
        """ Get a new half edge pair, after specifying its start and end.
            Can set the faces, and previous edges of the new edge pair. 
            Returns the outer edge
        """
        e1 = HalfEdge(originVertex,None)
        e2 = HalfEdge(twinVertex,e1)
        e1.twin = e2 #fixup
        if face:
            e1.face = face
            face.innerComponents.append(e1)
        if twinFace:
            e2.face = twinFace
            twinFace.innerComponents.append(e2)
        if prev:
            e1.prev = prev
            prev.next = e1
        if prev2:
            e2.prev = prev2
            prev2.next = e2
        self.halfEdges.extend([e1,e2])
        return e1
        
    def newFace(self):
        """ Creates a new face to link edges """
        newFace = Face()
        self.faces.append(newFace)
        return newFace

    def linkEdgesTogether(self,edges):
        for i,e in enumerate(edges):
            e.prev = edges[i-1]
            e.prev.next = e
    
    def setFaceForEdgeLoop(self,face,edge,isInnerComponentList=False):
        """ For a face and a list of edges, link them together
            If the edges are the outer components, just put the first edge in the face,
            Otherwise places all the edges in the face """
        start = edge
        current = edge.next
        if isInnerComponentList:
            face.innerComponents.append(start)
        else:
            face.outerComponent = start
        start.face = face
        while current is not start and current.next is not None:
            current.face = face
            current = current.next
            if isInnerComponentList:
                face.innerComponents.append(current)

                
    def orderVertices(self,focus,vertices):
        """ Given a focus point and a list of vertices, sort them
            by the counter-clockwise angle position they take relative """
        relativePositions = [[x-focus[0],y-focus[1]] for x,y in vertices]        
        angled = [(atan2(yp,xp),x,y) for xp,yp,x,y in zip(relativePositions,vertices)]
        sortedAngled = sorted(angled)        
        return sortedAngled

    def inferEdges(self,face,vertices):
        """ Given a face and a set of vertices belonging to face, 
            sort the vertices CCW and connect together in that order """
        return

    def discard_outbounds_vertices(self,bbox):
        """ Given a [x,y,x2,y2] bbox, discards all vertices not in the bbox   """
        self.vertices = [v for v in self.vertices if v.within(bbox)]


    def constrain_half_edges(self,bbox):
        """ For each halfedge, shorten it to be within the bounding box  """
        for e in self.halfEdges:
            #if both vertices are within the bounding box, don't touch
            if e.within(bbox):
                continue
            #if both vertices are out of the bounding box, clean away entirely
            elif e.outside(bbox):
                e.markedForCleanup = True
            else:
                #else constrain the point outside the bounding box:
                newBounds = e.constrain(bbox)
                #e.clearVertices()
                #e.addVertex()
                #e.addVertex()
                

        #todo: remove edges marked for cleanup
        
        #todo: remove vertices with no associated edges


    def complete_faces(self):
        for f in self.faces:
            #sort edges
            #set next and previous
            #for e in f.edges:
            ##if e.endpoint != e.next.startpoint:
            ###create new edge between the points
            ###taking into account corners
                
