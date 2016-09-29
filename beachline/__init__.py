### A Red-Black Tree bastardisation into a Beach Line for fortune's
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
class BeachLine(object):

    def __init__(self):
        """ Initialise the rb tree container, ie: the node list """
        self.nodes = []
        self.arcs_added = []
        self.root = None

    def update_arcs(self,d):
        for arc in self.arcs_added:
            arc.update_d(d)
        
    def isEmpty(self):
        if self.root is None:
            return True
        return False
        
    def insert_root(self,arc,data=None):
        self.root = Node((arc,arc))
        self.balance(self.root)
        self.arcs_added.append(arc)

    def delete_leaf(self,z):
        """ Delete a leaf, collapsing parents as necessary,  """
        if not z.isLeaf():
            raise Exception("Attempting to delete a non leaf")
        print("Deleting Leaf: ",z.left_arc)
        node_parent = z.parent
        #Base case: Root
        if node_parent is None and self.root == z:
            self.root = None
            return
        #General Case:        
        #transplant the opposite side to the parent
        if node_parent.left == z:
            transplant(self,node_parent,node_parent.right)
        else:
            transplant(self,node_parent,node_parent.left)
            #collapse if two arcs are of the same parabola:
        node_grand_parent = node_parent.parent
        while node_grand_parent is not None:
            node_parent = node_grand_parent.parent
            node_grand_parent = self.collapse_duplicate_arcs(node_grand_parent)
        #rebalance
        if node_parent:
            rbDeleteFixup(self,node_parent)
            #re-check inner node arcs:
            self.check_arcs(node_parent)

    def check_arcs(self,node):
        """ given a node, ensure it has the correct arcs 
            (max left + min right) for each parent chain
        """
        while node is not None:
            if node.isLeaf():
                node = node.parent
            else:
                node.left_arc = node.left.getMaxArc()
                node.right_arc = node.right.getMinArc()
                node = node.parent
            
        
    def delete(self,node):
        """ Delete a value from the tree """
        rbTreeDelete(self,node)

    def search(self,x,d=None):
        """ Search the tree for a value, getting closest node to it """
        current = self.root
        while not current.isLeaf():
            if current.breakpointComparison(x,d=d):
                current = current.left
            else:
                current = current.right
        return current
                
    def min(self):
        """ Get the min value of the tree """
        return self.root.getMin()

    def max(self):
        """ Get the max value of the tree """
        return self.root.getMax()

    def split(self,arc,existingNode):
        """ splice an arc in the middle of a single existing arc """
        self.arcs_added.append(arc)
        oldParent = existingNode.parent
        if oldParent is not None:
            if existingNode == oldParent.left:
                left_side_of_parent = True
            else:
                left_side_of_parent = False
        #creation:
        leaf1 = Node((existingNode.left_arc,existingNode.left_arc),side=LEFT)
        leaf2 = Node((arc,arc))
        leaf3 = Node((existingNode.left_arc,existingNode.left_arc),side=RIGHT)
        parent1 = Node((leaf1.getMaxArc(),leaf2.getMinArc()),colour=existingNode.colour)
        parent2 = Node((leaf2.getMaxArc(),leaf1.getMinArc()))
        #Linking:
        parent1.add_left(leaf1)
        parent2.add_left(leaf2)
        parent2.add_right(leaf3)
        parent1.add_right(parent2)
        if oldParent is not None:
            if left_side_of_parent:
                oldParent.add_left(parent1)
            else:
                oldParent.add_right(parent1)
        else:
            self.root = parent1
        #delete the exsiting node
        del existingNode
        #return the middle leaf
        return leaf2

    def balance(self,node):
        rbtreeFixup(self,node)
        #after fixing up colours, ensure integrity
        #of inner node references
        self.check_arcs(node)

    def get_chain(self):
        """ Get the arcs from leaves, left to right, as a list """
        if self.root is None:
            return []
        chain = []
        if type(self.root) is not Node:
            IPython.embed()
        current = self.root.getMin()
        while current is not None:
            if not current.isSingleArc():
                raise Exception("Chain isnt dealing with only leaves")
            if not current.left_arc.vertical_line \
               and (len(chain) == 0 or current.left_arc != chain[-1]):
                chain.append(current.left_arc)
            current = current.getSuccessor()
        return chain

    def collapse_duplicate_arcs(self,node):
        """ If a node has the same arc for left and right,
            just collapse them together, replacing the node with a leaf.
        """
        if node.left and node.right and \
           node.left.isSingleArc() and node.right.isSingleArc() and \
           node.left.left_arc == node.right.left_arc:
            if node.parent == None:
                self.root = node.left_arc
            elif node.parent.left == node:
                node.parent.add_left(node.left)
            else:
                node.parent.add_right(node.right)
            return node.parent
        else:
            return None
            
    def get_successor_triple(self,node):
        a = node
        b = a.getSuccessor()
        if b:
            c = b.getSuccessor()
        if a and b and c:
            return (a,b,c)
        else:
            return None

    def get_predecessor_triple(self,node):
        a = node
        b = a.getPredecessor()
        if b:
            c = b.getPredecessor()
        if a and b and c:
            return (a,b,c)
        else:
            return None
        
        
#--------------------
#Internal node
class Node(object):
    """ The internal node class for the rbtree.  """
    i = 0
    
    def __init__(self,value,parent=None,data=None,side=CENTRE,colour=RED):
        self.id = Node.i
        Node.i += 1
        #Node Data:
        self.colour = colour
        if len(value) < 2:
            raise Exception("Node expected a tuple")
        self.left_arc = value[0]
        self.right_arc = value[1]
        self.left_circle_event = None
        self.right_circle_event = None
        self.data = data
        self.side = side
        #Children:
        self.left = None
        self.right = None
        #Parent:
        self.parent = parent
        #successor
        self.successor = None
        #predecessor
        self.predecessor = None

    def breakpointComparison(self,x,d=None):
        if self.isSingleArc():
            return self.left_arc.is_left_of_focus(x)
        if d:
            self.update_arcs(d)
        existing_intersect = self.left_arc.intersect(self.right_arc)
        if len(existing_intersect) == 0:
            raise Exception("No intersection")
        elif len(existing_intersect) == 1:
            return x < existing_intersect[0][0]
        else:
            return x < existing_intersect[:,0].min()


    def countBlackHeight(self):
    """ Given a node, count all paths and check they have the same black height """
    stack = [self]
    leaves = []
    while len(stack) > 0:
        current = stack.pop()
        if current.isLeaf():
            leaves.append(current)
        else:
            if current.left is not None:
                stack.append(current.left)
            if current.right is not None:
                stack.append(current.right)

    allHeights = [x.getBlackHeight(self) for x in leaves]
    return allHeights
        
    def isSingleArc(self):
        return self.left_arc == self.right_arc

    def isLeaf(self):
        return self.left == None and self.right == None
    
    def intersect(self,node):
        raise Exception("Not implemented yet: intersect")

    def update_arcs(self,d):
        if self.left_arc:
            self.left_arc.update_d(d)
        if self.right_arc and self.right_arc != self.left_arc:
            self.right_arc.update_d(d)
        
    def getBlackHeight(self,parent=None):
        """ Get the number of black nodes from self to the root  """
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
        """ String representation of the node """
        if self.colour == RED:
            colour = "R"
        else:
            colour = "B"
        return "({}_{} {} {})".format(colour,self.value,self.left,self.right)

    def getMin(self):
        """ Get the smallest leaf from the subtree this node is root of """
        current = self
        while current.left is not None:
            current = current.left
        return current
    
    def getMax(self):
        """ Get the largest leaf from the subtree this node is root of """
        current = self
        while current.right is not None:
            current = current.right
        return current

    def getMinArc(self):
        return self.getMin().left_arc

    def getMaxArc(self):
        return self.getMax().right_arc
    
    def getPredecessor(self):
        """ Get the nearest leaf thats to the left of self """
        if self.left is not None:
            return self.left.getMax()
        else:
            current = self
            while current.parent is not None and current.parent.right != current:
                current = current.parent
                
            if current.parent is not None:
                current = current.parent
            else:
                return None
            if current.left is not None:
                proposedPredecessor = current.left.getMax()
                if proposedPredecessor != self:
                    return current.left.getMax()
        return None

    def getSuccessor(self):
        """ Get the nearest leaf thats to the right of self  """
        #print("Getting successor of {}".format(self.id))
        if self.right is not None:
            return self.right.getMin()
        else:
            current = self
            while current.parent is not None and current.parent.left != current:
                current = current.parent
                
            if current.parent is not None:
                current = current.parent
            else:
                return None
            if current.right is not None:
                proposedSuccessor = current.right.getMin()
                if proposedSuccessor != self:
                    return proposedSuccessor
        return None

    def add_left(self,node):
        self.left = node
        if node is not None:
            self.left.parent = self
            self.left_arc = self.left.getMaxArc()

    def add_right(self,node):
        self.right = node
        if node is not None:
            self.right.parent = self
            self.right_arc = self.right.getMinArc()
        
#--------------------
# Helper functions

def rotateLeft(tree,node):
    """ Rotate the given node left, making the new head be node.right """
    if node.right is None:
        return
    newHead = node.right #Get the right subtree
    originalParent = node.parent
    node.add_right(newHead.left)       #left subtree becomes the right subtree
    newHead.add_left(node)             #move the original node to the left
    if originalParent is None:            #update the root of the tree
        newHead.parent = None
        tree.root = newHead
    elif node == originalParent.left:  #update the parent's left subtree
        originalParent.add_left(newHead)
    else:
        originalParent.add_right(newHead)

def rotateRight(tree,node):
    """ Rotate the given node right, making the new head be node.left """
    if node.left is None:
        return
    newHead = node.left
    originalParent = node.parent
    node.add_left(newHead.right)
    newHead.add_right(node)
    if originalParent is None:
        newHead.parent = None
        tree.root = newHead
    elif node == originalParent.left:
        originalParent.add_left(newHead)
    else:
        originalParent.add_right(newHead)

def rbtreeFixup(tree,node):
    """ Verify and fix the RB properties hold """
    while node.parent is not None and node.parent.colour == RED:
        parent = node.parent
        grandParent = parent.parent
        if grandParent is None:
            break
        elif parent == grandParent.left:
            y = grandParent.right
            if y is not None and y.colour == RED:
                parent.colour = BLACK
                y.colour = BLACK
                grandParent.colour = RED
                node = grandParent
            else:
                if node == parent.right:
                    node = parent
                    rotateLeft(tree,node)
                parent.colour = BLACK
                grandParent.colour = RED
                rotateRight(tree,grandParent)
        else:
            y = grandParent.left
            if y is not None and y.colour == RED:
                parent.colour = BLACK
                y.colour = BLACK
                grandParent.colour = RED
                node = grandParent
            else:
                if node == parent.left:
                    node = parent
                    rotateRight(tree,node)
                parent.colour = BLACK
                grandParent.colour = RED
                rotateLeft(tree,grandParent)
    tree.root.colour = BLACK

def transplant(tree,u,v):
    """ Transplant the node v, and its subtree, in place of node u """
    if u.parent is None:
        tree.root = v
    elif u == u.parent.left:
        u.parent.add_left(v)
    else:
        u.parent.add_right(v)
    del u


def rbTreeDelete(tree,z):
    """ Delete the node z from the tree,
        modified to delete the parent it necessary
    z = the node to delete
    y = the current node?
    x = chosen subtree?
    """
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
    """ After deleting a node, verify the RB properties hold """
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
            
            

        

