### A Red-Black Tree Implementation
# Properties of RBTrees:
# 1) Every node is Red Or Black
# 2) The root is black
# 3) Every leaf is Black, leaves are null nodes
# 4) If a node is red, it's children are black
# 5) All paths from a node to its leaves contain the same number of black nodes



#Constants of colours
RED = 0
BLACK = 1

#Container
class RBTree(object):

    def __init__(self):
        """ Initialise the rb tree container, ie: the node list """
        self.nodes = []
        self.root = None
        self.nextId = 0

    def isEmpty(self):
        if self.root is None:
            return True
        return False
        
    def insert(self,*args):
        for x in args:
            self.rb_insert(x)
        
    def rb_insert(self,value,data=None):
        """ Insert a value into the tree """
        newNode = Node(self.nextId,value,data=data)
        self.nodes.append(newNode)
        self.nextId += 1
        
        y = None
        x = self.root
        
        while x is not None:
            y = x
            if newNode.value < x.value:
                x = x.left
            else:
                x = x.right
        newNode.parent = y
        if y is None:
            self.root = newNode
        elif newNode.value < y.value:
            y.left = newNode
        else:
            y.right = newNode
        newNode.left = None
        newNode.right = None
        rbtreeFixup(self,newNode)

    def delete(self,node):
        """ Delete a value from the tree """
        rbTreeDelete(self,node)

    def search(self,value):
        """ Search the tree for a value, getting closest node to it """
        current = self.root
        while current is not None and current.value != value:
            if value > current.value:
                if current.right is not None:
                    current = current.right
                else:
                    return current
            else:
                if current.left is not None:
                    current = current.left
                else:
                    return current
        return current
                
    def min(self):
        """ Get the min value of the tree """
        return self.root.getMin()

    def max(self):
        """ Get the max value of the tree """
        return self.root.getMax()
    
#--------------------
#Internal node
class Node(object):

    def __init__(self,id,value,parent=None,data=None):
        self.id = id
        #Children:
        self.left = None
        self.right = None
        #Parent:
        self.parent = parent
        #successor
        self.successor = None
        #predecessor
        self.predecessor = None
        #Node Date:
        self.colour = RED
        self.value = value
        self.data = data

    def getBlackHeight(self,parent=None):
        current = self
        height = 0
        while current is not None:
            if current.colour == BLACK:
                height += 1
            if current == parent:
                current = None
            else:
                current = current.parent
        return height
        
    def __str__(self):
        if self.colour == RED:
            colour = "R"
        else:
            colour = "B"
        return "({}_{} {} {})".format(colour,self.value,self.left,self.right)

    def getMin(self):
        current = self
        while current.left is not None:
            current = current.left
        return current

    def getMax(self):
        current = self
        while current.right is not None:
            current = current.right
        return current

    def getPredecessor(self):
        if self.left is not None:
            return self.left.getMax()
        else:
            current = self
            while current.parent is not None and current.parent.right != current:
                current = current.parent
            if current.parent is not None:
                current = current.parent
            if current.value <= self.value:
                return current
            else:
                return None

    def getSuccessor(self):
        if self.right is not None:
            return self.right.getMin()
        else:
            current = self
            while current.parent is not None and current.parent.left != current:
                current = current.parent
            if current.parent is not None:
                current = current.parent
            if current.value >= self.value:
                return current
            else:
                return None
    
#--------------------
# Helper functions

def rotateLeft(tree,node):
    """ Rotate the given node left, making the new head be node.right """
    if node.right is None:
        return
    newHead = node.right #Get the right subtree
    node.right = newHead.left        #left subtree becomes the right subtree 
    if newHead.left is not None:     #update the parent of the left subtree
        newHead.left.parent = node
    newHead.parent = node.parent     #update the parent of the new head
    if node.parent is None:          #update the root of the tree
        tree.root = newHead
    elif node == node.parent.left:  #update the parent's left subtree
        node.parent.left = newHead
    else:
        node.parent.right = newHead #update the parent's right subtree
    newHead.left = node           #move the original node to the left
    node.parent = newHead         #update the parent of the original node


def rotateRight(tree,node):
    """ Rotate the given node right, making the new head be node.left """
    if node.left is None:
        return
    newHead = node.left
    node.left = newHead.right
    if newHead.right is not None:
        newHead.right.parent = node
    newHead.parent = node.parent
    if node.parent is None:
        tree.root = newHead
    elif node == node.parent.right:
        node.parent.right = newHead
    else:
        node.parent.left = newHead
    newHead.right = node
    node.parent = newHead

def rbtreeFixup(tree,node):
    while node.parent is not None and node.parent.colour == RED:
        parent = node.parent
        parentParent = parent.parent
        if parentParent is None:
            break
        elif parent == parentParent.left:
            y = parentParent.right
            if y is not None and y.colour == RED:
                parent.colour = BLACK
                y.colour = BLACK
                parentParent.colour = RED
                node = parentParent
            else:
                if node == parent.right:
                    node = parent
                    rotateLeft(tree,node)
                parent.colour = BLACK
                parentParent.colour = RED
                rotateRight(tree,parentParent)
        else:
            y = parentParent.left
            if y is not None and y.colour == RED:
                parent.colour = BLACK
                y.colour = BLACK
                parentParent.colour = RED
                node = parentParent
            else:
                if node == parent.left:
                    node = parent
                    rotateRight(tree,node)
                parent.colour = BLACK
                parentParent.colour = RED
                rotateLeft(tree,parentParent)
    tree.root.colour = BLACK

def countBlackHeight(node):
    """ Given a node, count all paths and check they have the same black height """
    stack = [node]
    leaves = []
    while len(stack) > 0:
        current = stack.pop()
        if current.left is None and current.right is None:
            leaves.append(current)
        else:
            if current.left is not None:
                stack.append(current.left)
            if current.right is not None:
                stack.append(current.right)

    allHeights = [x.getBlackHeight(node) for x in leaves]
    return allHeights


def transplant(tree,u,v):
    """ Transplant the node v, and its subtree, in place of node u """
    if u.parent is None:
        tree.root = v
    elif u == u.parent.left:
        u.parent.left = v
    else:
        u.parent.right = v
    v.parent = u.parent
    

def rbTreeDelete(tree,z):
    """ Delete the node z from the tree """
    y = z
    origColour = y.colour
    x = None
    if z.left is None: #no left subtree, just move the right up
        x = z.right
        transplant(tree,z,z.right) 
    elif z.right is None: #no right subtree, move the left up
        x = z.left
        transplant(tree,z,z.left)
    else: #both subtrees exist
        y = z.right.getMin() #get the min of the right, and use that in place of the old head
        #could use the max of the left? might conflict with colours
        origColour = y.colour 
        x = y.right 
        if y.parent == z: #degenerate case: min of tree is z.right
            if x is not None:
                x.parent = y # surely this is redundant? x is already a child of y?
        else:
            transplant(tree,y,y.right) #move y'right subtree to where y is
            y.right = z.right #move the right subtree of the node to delete to the min of that subtree
            y.right.parent = y #update the parent
        transplant(tree,z,y) #move the new minimum to where z was
        y.left = z.left #take z's left subtree, move it to y
        y.left.parent = y #update the parent of the left subtree
        y.colour = z.colour #copy the colour over
    if origColour == BLACK:
        rbDeleteFixup(tree,x)


def rbDeleteFixup(tree,x):
    while x != tree.root and x.colour == BLACK: #keep going till you hit the root
        if x == x.parent.left: #Operate on the left subtree
            w = x.parent.right 
            if w.colour == RED: # opposite subtree is red
                w.colour = BLACK #switch colour of that tree and parent
                x.parent.colour = RED 
                rotateLeft(tree,x.parent) #then rotate
                w = x.parent.right #update the the opposite subtree to the new subtree
            if w.left.colour == BLACK and w.right.colour == BLACK: #if both subtrees are black
                w.colour = RED #recolour the subtree head
                x = x.parent #and move up
            else: #different colours on the subtrees
                if w.right.colour == BLACK: 
                    w.left.colour = BLACK #normalise the colours of the left and right
                    w.colour = RED #flip the parent colour
                    rotateRight(tree,w) #rotate
                    w = x.parent.right #update the subtree focus 
                w.colour = x.parent.colour 
                x.parent.colour = BLACK
                w.right.colour = BLACK
                rotateLeft(tree,x.parent) #rotate back if necessary
                x = tree.root 
        else: #mirror image for right subtree
            w = x.parent.left
            if w.colour == RED:
                w.colour = BLACK
                x.parent.colour = RED
                rotateRight(tree,x.parent)
                w = x.parent.left
            if w.right.colour == BLACK and w.left.colour == BLACK:
                w.colour = RED
                x = x.parent
            elif w.left.colour == BLACK:
                w.right.colour = BLACK
                w.colour = RED
                rotateLeft(tree,w)
                w = x.parent.left
            w.colour = x.parent.colour
            x.parent.colour = BLACK
            w.left.colour = BLACK
            rotateRight(tree,x.parent)
            x = Tree.root
    x.colour = BLACK
            
            
