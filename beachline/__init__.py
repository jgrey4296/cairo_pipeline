## A Red-Black Tree bastardisation into a Beach Line for fortune's
# Properties of RBTrees:
# 1) Every node is Red Or Black
# 2) The root is black
# 3) Every leaf is Black, leaves are null nodes
# 4) If a node is red, it's children are black
# 5) All paths from a node to its leaves contain the same number of black nodes

from string import ascii_uppercase
import IPython
import numpy as np
import utils
import math
import logging

#--------------------
#def Beachline Container
#--------------------
class BeachLine(object):

    def __init__(self,arc=True):
        """ Initialise the rb tree container, ie: the node list """
        self.arc = arc
        self.nodes = []      #list of all nodes created 
        self.arcs_added = [] #list of all values added
        self.root = None

    def __str__(self):
        if self.root is None:
            return "_"
        else:
            str = []
            str.append("RB Tree:\n")
            str.append("Colours: " + self.root.print_colour() + "\n")
            str.append("Heights: " + self.root.print_blackheight() + "\n")
            str.append("P_ids: " + self.root.print_parabola_id() + "\n")
            str.append("Chain ids: " + self.print_chain())
            return "".join(str)
                
    def print_chain(self):
        if not self.arc:
            lst = [str(x) for x in self.get_chain()]
        else:
            lst = [ascii_uppercase[x.value.id] for x in self.get_chain()]
        return "-".join(lst)
        
    def update_arcs(self,d):
        for arc in self.arcs_added:
            arc.update_d(d)
        
    def isEmpty(self):
        if self.root is None:
            return True
        return False

    def insert_many(self,*values):
        for x in values:
            self.insert(x)
    
    def insert(self,value):
        if self.root is None:
            self.insert_successor(None,value)
        else:
            node,direction = self.search(value)
            if isinstance(direction,Right) or isinstance(direction,Centre):
                self.insert_successor(node,value)
            else: #isinstance(direction,Left):
                self.insert_predecessor(node,value)
        
    def insert_successor(self,existing_node,newValue):
        self.arcs_added.append(newValue)
        new_node = Node(newValue,arc=self.arc)
        self.nodes.append(new_node)
        if existing_node is None:
            existing_node = self.root
        if existing_node is None:
            self.root = new_node
        else:
            existing_node.add_right(new_node)
        self.balance(new_node)
        return new_node

    def insert_predecessor(self,existing_node,newValue):
        self.arcs_added.append(newValue)
        new_node = Node(newValue,arc=self.arc)
        self.nodes.append(new_node)
        if existing_node is None:
            existing_node = self.root
        if existing_node is None:
            self.root = new_node
        else:
            existing_node.add_left(new_node)
        self.balance(new_node)
        return new_node

    def delete_value(self,value):
        node,direction = self.search(value)
        self.delete_node(node)
        
    
    def delete_node(self,node):
        """ Delete a value from the tree """
        if self.arc:
            triple = [node.predecessor,node,node.successor]
            tripleString = "-".join([ascii_uppercase[x.value.id] for x in triple if x])
            logging.info("Deleting Arc: {}".format(tripleString))
        else:
            logging.info("Deleting Value: {}".format(node.value))
            
        rbTreeDelete_textbook(self,node)
        self.nodes.remove(node)

    def search(self,x,d=None,verbose=False):
        """ Search the tree for a value, getting closest node to it, 
            returns (node,insertion_function)
        """
        current = self.root
        if current is None:
            return None #not found
        parent = None
        found = False
        while not found:
            comp = current.compare(x,d=d)
            logging.debug("Moving: {}".format(comp))
            if isinstance(comp,Left):
                parent = current
                current = current.left
            elif isinstance(comp,Right):
                parent = current
                current = current.right
            elif isinstance(comp,Centre):
                #ie: spot on
                parent = current
                found = True
            else: #type is none
                raise Exception("Comparison returned None")
            if current is None:
                found = True
                
        return (parent, comp) #the existing parent and the side to add it
        
    def min(self):
        """ Get the min value of the tree """
        if self.root is None:
            return None
        return self.root.getMin()

    def max(self):
        """ Get the max value of the tree """
        if self.root is None:
            return None
        return self.root.getMax()
        
    def balance(self,node):
        rbtreeFixup(self,node)

    def get_chain(self):
        """ Get the sequence of values, from left to right """
        if self.root is None:
            return []
        chain = []
        current = self.root.getMin()
        while current is not None:
            logging.debug("Get_chain: appending {}".format(current))
            chain.append(current)
            current = current.successor
        return [x for x in chain]

    def collapse_adjacent_arcs(self,node):
        """ If a node has the same arc as a successor/predecessor,
            just collapse them together, deleting one node
        """
        raise Exception
            
    def get_successor_triple(self,node):
        if node is None:
            return None
        a = node
        b = a.successor
        if b:
            c = b.successor
            if a and b and c:
                return (a,b,c)
        return None

    def get_predecessor_triple(self,node):
        if node is None:
            return None
        a = node
        b = a.predecessor
        if b:
            c = b.predecessor
            if a and b and c:
                return (c,b,a)
        return None
        
    def countBlackHeight(self,node=None):
        """ Given a node, count all paths and check they have the same black height """
        if node is None:
            if self.root is None:
                return None
        node = self.root
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
    
#--------------------
#def Internal node
#--------------------

class Node(object):
    """ The internal node class for the rbtree.  """
    i = 0
    
    def __init__(self,value,parent=None,data=None,red=True,arc=True):
        self.id = Node.i
        Node.i += 1
        #Node Data:
        self.red = red
        #arc: is the value an arc or a normal number?
        self.arc = arc
        self.value = value
        self.left_circle_event = None
        self.right_circle_event = None
        self.data = data
        #Children:
        self.left = None
        self.right = None
        #Parent:
        self.parent = parent
        #successor
        self.successor = None
        #predecessor
        self.predecessor = None

    def __str__(self):
        if self.arc:
            return ascii_uppercase[self.value.id]
        else:
            return str(self.value)

    def compare_simple(self,x):
        if x < self.value:
            return Left()
        if x > self.value:
            return Right()
        return Centre()
        
    def compare(self,x,d=None):
        logging.debug("Comparing {} to {}".format(x,self))
        if not self.arc:
            return self.compare_simple(x)
        
        pred = self.predecessor
        succ = self.successor
        logging.debug("Pred: {}, Succ: {}".format(pred,succ))
        pred_intersect = None
        succ_intersect = None
        the_range = [-math.inf,math.inf]
        if pred is None and succ is None: #Base case: single arc
            logging.debug("Single Arc: {}".format(self))
            return Centre()

        if pred and succ:
            logging.debug("Trio of arcs is clockwise: {}".format(utils.isClockwise(pred.value.get_focus(),\
                                                                           self.value.get_focus(),\
                                                                           succ.value.get_focus(),\
                                                                           cartesian=True)))
        #pred and successor are the same arc
        if pred and succ and pred.value == succ.value:
            intersect = pred.value.intersect(self.value)
            logging.warning("Predecessor and Successor are the same: {}".format(pred))
            logging.debug("Intersection result: {}".format(intersect))
            if len(intersect) != 2:
                raise Exception("Two parabolas arent intersecting correctly")
            if the_range[0] < intersect[:,0].min():
                the_range[0] = intersect[:,0].min()
            if the_range[1] > intersect[:,0].max():
                the_range[1] = intersect[:,0].max()
            

        else: #different arcs bookend
            if pred is not None:
                pred_intersect = self.value.intersect(pred.value)
                logging.debug("Pred intersect result: {}".format(pred_intersect))
                if len(pred_intersect) > 0:
                    the_range[0] = pred_intersect[1,0]
                    
            
            if succ is not None:
                succ_intersect = succ.value.intersect(self.value)
                logging.debug("Succ intersect result: {}".format(succ_intersect))
                if len(succ_intersect) > 0:
                    the_range[1] = succ_intersect[1,0]

        logging.debug("Testing: {} < {} < {}".format(the_range[0],x,the_range[1]))
        if the_range[0] < x and x <= the_range[1]:
            return Centre()
        elif x < the_range[0]:
            return Left()
        elif the_range[1] < x:
            return Right()
        else:
            raise Exception("Comparison failure")

        
    def isLeaf(self):
        return self.left == None and self.right == None
    
    def intersect(self,node):
        if not self.arc or not node.arc:
            raise Exception("Cant intersect on a non-arc node")
        else:
            raise Exception("Not implemented yet: intersect")

    def update_arcs(self,d):
        if not self.arc:
            raise Exception("Can't update arc on a non-arc node")
        self.arc.update_d(d)
        
    def getBlackHeight(self,root=None):
        """ Get the number of black nodes from self to the root  """
        current = self
        height = 0
        while current is not None:
            if not current.red:
                height += 1
            if current == root:
                current = None
            else:
                current = current.parent
        return height

    def countBlackHeight_null_add(self):
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

        #plus one for the true 'leaf' nodes, the nill ones
        allHeights = [x.getBlackHeight(self)+1 for x in leaves]
        return allHeights
    
    def print_colour(self):
        """ String representation of the node """
        if self.red:
            colour = "R"
        else:
            colour = "B"
        if self.isLeaf():
            return "{}".format(colour)
        else:
            a = None
            b = None
            if self.left:
                a = self.left.print_colour()
            if self.right:
                b = self.right.print_colour()
            return "{}( {} {} )".format(colour,a,b)

    def print_blackheight(self):
        if self.isLeaf():
            return "{}".format(self.getBlackHeight())
        else:
            a = None
            b = None
            if self.left:
                a = self.left.print_blackheight()
            if self.right:
                b = self.right.print_blackheight()
            return "{}( {} {})".format(self.getBlackHeight(), a,b)
        
    def print_parabola_id(self):
        if not self.arc:
            return ""
        elif self.isLeaf():
            return ascii_uppercase[self.value.id]
        else:
            i = ascii_uppercase[self.value.id]
            a = None
            b = None
            if self.left:
                a = self.left.print_parabola_id()
            if self.right:
                b = self.right.print_parabola_id()
            return "{}( {} {} )".format(i,a,b)

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

    def getMinValue(self):
        return self.getMin().value

    def getMaxValue(self):
        return self.getMax().value
    
    def add_left(self,node,force=False):
        logging.debug("{}: Adding {} to Left".format(self,node))
        if self.left is None or force:
            oldPred = self.predecessor
            self.link_left(node)
            self.link_predecessor(self.left.getMax())
            if oldPred:
                oldPred.link_successor(self.left.getMin())
        else:
            self.predecessor.add_right(node)
        
    def add_right(self,node,force=False):
        logging.debug("{}: Adding {} to Right".format(self,node))
        if self.right is None or force:
            oldSucc = self.successor
            self.link_right(node)
            self.link_successor(self.right.getMin())
            if oldSucc:
                oldSucc.link_predecessor(self.right.getMax())
        else:
            self.successor.add_left(node)
        
    def disconnect_from_parent(self):
        if self.parent:
            if self.parent.left == self:
                logging.debug("Disconnecting {} L-> {}".format(self.parent,self))
                self.parent.left = None
            else:
                logging.debug("Disconnecting {} R-> {}".format(self.parent,self))
                self.parent.right = None
            self.parent = None

    def link_left(self,node):
        logging.debug("{} L-> {}".format(self,node))
        self.left = node
        if self.left:
            self.left.parent = self

    def link_right(self,node):
        logging.debug("{} R-> {}".format(self,node))
        self.right = node
        if self.right:
            self.right.parent = self
            
    def disconnect_sequence(self):
        self.disconnect_successor()
        self.disconnect_predecessor()

    def disconnect_hierarchy(self):
        return [self.disconnect_left(),self.disconnect_right()]
            
    def disconnect_successor(self):
        logging.debug("Disconnecting {} successor {}".format(self,self.successor))
        if self.successor:
            self.successor.predecessor = None
            self.successor = None

    def disconnect_predecessor(self):
        logging.debug("Disconnecting {} predecessor {}".format(self,self.predecessor))
        if self.predecessor:
            self.predecessor.successor = None
            self.predecessor = None

    def link_successor(self,node):
        logging.debug("Linking {} Successor: {}, Cancelling: {}".format(self,node,self.successor))
        self.successor = node
        if self.successor:
            self.successor.predecessor = self

    def link_predecessor(self,node):
        logging.debug("Linking {} Predecessor: {}, Cancelling: {}".format(self,node,self.predecessor))
        self.predecessor = node
        if self.predecessor:
            self.predecessor.successor = self
        
    def disconnect_left(self):
        logging.debug("{} disconnectin left: {}".format(self,self.left))
        if self.left:
            node = self.left
            self.left = None
            node.parent = None
            return node
        return None

    def disconnect_right(self):
        logging.debug("{} disconnecting right: {}".format(self,self.right))
        if self.right:
            node = self.right
            self.right = None
            node.parent = None
            return node
        return None
            
#--------------------
# def Helper functions
#--------------------

def rotateLeft(tree,node):
    """ Rotate the given node left, making the new head be node.right """
    if node is None or node.right is None:
        return
        #raise Exception("Rotating left when there is no right")
    newHead = node.right #Get the right subtree
    originalParent = node.parent
    #left subtree becomes the right subtree:
    node.right = newHead.left
    if node.right:
        node.right.parent = node
    #move the original node to the left
    newHead.left = node
    newHead.left.parent = newHead
    if originalParent is None:            #update the root of the tree
        newHead.parent = None
        if tree:
            tree.root = newHead
    elif node == originalParent.left:  #update the parent's left subtree
        originalParent.left = newHead
        newHead.parent = originalParent
    else:
        originalParent.right = newHead
        newHead.parent = originalParent
    return newHead

def rotateRight(tree,node):
    """ Rotate the given node right, making the new head be node.left """
    if node is None or node.left is None:
        raise Exception("Rotating right when there is no left")
    newHead = node.left
    originalParent = node.parent
    node.left = newHead.right
    if node.left:
        node.left.parent = node
    newHead.right = node
    newHead.right.parent = newHead    
    if originalParent is None:
        newHead.parent = None
        if tree:
            tree.root = newHead
    elif node == originalParent.left:
        originalParent.left = newHead
        newHead.parent = originalParent
    else:
        originalParent.right = newHead
        newHead.parent = originalParent
    return newHead
        
def rbtreeFixup(tree,node):
    """ Verify and fix the RB properties hold """
    while node.parent is not None and node.parent.red:
        parent = node.parent
        grandParent = parent.parent
        if grandParent is None:
            break
        elif parent == grandParent.left:
            y = grandParent.right
            if y is not None and y.red:
                parent.red = False
                y.red = False
                grandParent.red = True
                node = grandParent
            else:
                if node == parent.right:
                    node = parent
                    rotateLeft(tree,node)#invalidates parent and grandparent
                node.parent.red = False
                node.parent.parent.red = True
                rotateRight(tree,node.parent.parent)
        else:
            y = grandParent.left
            if y is not None and y.red:
                parent.red = False
                y.red = False
                grandParent.red = True
                node = grandParent
            else:
                if node == parent.left:
                    node = parent
                    rotateRight(tree,node)#invalidates parent and grandparent
                node.parent.red = False
                node.parent.parent.red = True
                rotateLeft(tree,node.parent.parent)
    tree.root.red = False

def transplant(tree,u,v):
    """ Transplant the node v, and its subtree, in place of node u """
    if u.parent is None:
        tree.root = v
        if v is None:
            return
        if v.left:
            v.link_predecessor(v.left.getMax())
        else:
            v.link_predecessor(None)
        if v.right:
            v.link_successor(v.right.getMin())
        else:
            v.link_successor(None)
    elif u == u.parent.left:
        u.parent.link_left(v)
        if v is None:
            u.parent.predecessor = None
        else:
            v.parent.link_predecessor(v.getMax())
    else:
        u.parent.link_right(v)
        if v is None:
            u.parent.successor = None
        elif v.left:
            v.parent.link_successor(v.getMin())



def rbTreeDelete_textbook(tree,z):
    orig_parent = z.parent
    y = z
    y_originally_red = y.red
    x = None
    if z.left == None:
        x = z.right
        transplant(tree,z,z.right)
    elif z.right == None:
        x = z.left
        transplant(tree,z,z.left)
    else:
        y = z.right.getMin()
        y_originally_red = y.red
        x = y.right
        if y.parent == z:
            if x:
                x.parent = y
        else:
            transplant(tree,y,y.right)
            y.link_right(z.right)
            y.link_successor(z.right.getMin())
        transplant(tree,z,y)
        y.link_left(z.left)
        y.link_predecessor(z.left.getMax())
        y.red = z.red
    if not y_originally_red:
        rbDeleteFixup_textbook(tree,x)    
    del z
    #collapse when two nodes are the same
    if y and y.successor and y.value == y.successor.value:
        tree.delete(y.successor)
    elif y and y.predecessor and y.value == y.predecessor.value:
        tree.delete(y.predecessor)



def rbDeleteFixup_textbook(tree,x):
    while x is not None and x != tree.root and not x.red:
        if x == x.parent.left:
            w = x.parent.right
            if w.red:
                w.red = False
                x.parent.red = True
                rotateLeft(tree,x.parent)
                w = x.parent.right
            if (w.left is None or not w.left.red) and (w.right is None or not w.right.red):
                w.red = True
                x = x.parent
            else:
                if not w.right.red:
                    w.left.red = False
                    w.red = True
                    rotateRight(tree,w)
                    w = x.parent.right
                if x.parent:
                    w.red = x.parent.red
                    x.parent.red = False
                if w.right:
                    w.right.red = False
                rotateLeft(tree,x.parent)
                x = tree.root
        else: #mirror for right
            w = parent.left
            if w.red:
                w.red = False
                x.parent.red = True
                rotateRight(tree,x.parent)
                w = x.parent.left
            if (w.right is None or not w.right.red) and (w.left is None or not w.left.red):
                w.red = True
                x = x.parent
            else:
                if not w.left.red:
                    w.right.red = False
                    w.red = True
                    rotateLeft(tree,w)
                    w = x.parent.left
                if x.parent:
                    w.colour = x.parent.colour
                    x.parent.red = False
                if w.left:
                    w.left.red = False
                rotateRight(tree,x.parent)
                x = tree.root
    if x:
        x.red = False
        
# def rbDeleteFixup(tree,x):
#     """ After deleting a node, verify the RB properties hold """
#     while x is not None and x != tree.root and not x.red: #keep going till you hit the root
#         if x == x.parent.left: #Operate on the left subtree
#             w = x.parent.right 
#             if w.red: # opposite subtree is red
#                 w.red = False #switch colour of that tree and parent
#                 x.parent.red = True
#                 rotateLeft(tree,x.parent) #then rotate
#                 w = x.parent.right #update the the opposite subtree to the new subtree
#             if (w.left is None or not w.left.red) and (w.right is None or not w.right.red): #if both subtrees are black
#                 w.red = True #recolour the subtree head
#                 x = x.parent #and move up
#             else: #different colours on the subtrees
#                 if not w.right.red:
#                     w.left.red = False #normalise the colours of the left and right
#                     w.red = True #flip the parent colour
#                     rotateRight(tree,w) #rotate
#                     w = x.parent.right #update the subtree focus
#                 if x.parent is not None:
#                     w.red = x.parent.red 
#                     x.parent.red = False
#                 if w.right is not None:
#                     w.right.red = False
#                 rotateLeft(tree,x.parent) #rotate back if necessary
#                 x = tree.root 
#         else: #mirror image for right subtree
#             w = x.parent.left
#             if w.red:
#                 w.red = False
#                 x.parent.red = True
#                 rotateRight(tree,x.parent)
#                 w = x.parent.left
#             if w is None:
#                 continue
#             if (w.right is None or not w.right.red) and (w.left is None or not w.left.red):
#                 w.red = True
#                 x = x.parent
#             elif not w.left.red:
#                 w.right.red = False
#                 w.red = True
#                 rotateLeft(tree,w)
#                 w = x.parent.left
#             if x.parent is not None:
#                 w.red = x.parent.red
#                 x.parent.red = False
#             if w.left is not None:
#                 w.left.red = False
#             rotateRight(tree,x.parent)
#             x = tree.root
#     if x is not None:
#         x.red = False

def rbTreeDelete(tree,z):
    logging.info("rbTreeDelete: {}".format(z))
    parent = z.parent
    predecessor = z.predecessor
    if predecessor:
        predecessor.disconnect_successor()
    successor = z.successor
    if successor:
        successor.disconnect_predecessor()
    left = z.left
    right = z.right
    replacement = None
    sideLeft = False
    onParentsRight = parent and parent.right == z

    #shortcut for deleting a leaf
    if z.isLeaf():
        logging.debug("Deleting a leaf: {}".format(z))
        z.disconnect_sequence()
        z.disconnect_from_parent()
        if predecessor:
            predecessor.link_successor(successor)
            logging.debug("Linking: {} with {}".format(predecessor,successor))
    elif successor is not None and (successor.left is None or (successor.left and successor.left.getMax() != z)):
        logging.debug("Deleting {}".format(z))
        z.disconnect_sequence()
        z.disconnect_from_parent()
        replacement = successor
        replacement_successor = replacement.successor
        logging.debug("Replacing with {}".format(replacement))
        #delink the replacement's parent
        replacement.disconnect_from_parent()
        replacement.disconnect_sequence()
        #link z's predecessor to replacement
        replacement.link_predecessor(predecessor)
        logging.debug("Linking Predecessor {} to {}".format(predecessor,replacement))
        #link the replacement to the original parent
        if parent:
            logging.debug("Linking parent {} to {}".format(parent,replacement))
            if onParentsRight:
                parent.link_right(replacement)
                parent.link_successor(replacement.getMin())
            else:
                parent.link_left(replacement)
                parent.link_predecessor(replacement.getMax())
        else:
            tree.root = replacement
        #link the replacement to the right of the old node:
        if right and right != replacement:
            logging.debug("{} : Linking subtree {}".format(replacement,right))
            replacement.link_right(right)
            replacement.link_successor(right.getMin())
        else:
            replacement.link_successor(replacement_successor)            
        #link left:
        logging.debug("{}: Linking subtree: {}".format(replacement,left))
        if left:
            replacement.link_left(left)
            replacement.link_predecessor(left.getMax())
    elif predecessor: #no successor:
        z.disconnect_sequence()
        z.disconnect_from_parent()
        replacement = predecessor
        r_left = replacement.disconnect_left()
        r_parent = replacement.parent
        r_onParentsRight = r_parent and r_parent.right == replacement
        #delink the replacement's parent
        replacement.disconnect_successor()
        replacement.disconnect_from_parent()
        if parent is not None:
            if onParentsRight:
                parent.link_right(replacement)
            else:
                parent.link_left(replacement)
        else:
            tree.root = replacement
        #no link right, as no successor
        if successor:
            replacement.link_successor(successor)
        #link left
        if left is not None and left != replacement:
            replacement.link_left(left)
            replacement.link_predecessor(left.getMax())
        if r_left and r_parent and r_parent != z:
            if r_onParentsRight:
                r_parent.link_right(r_left)
                r_parent.link_successor(r_left.getMin())
            else:
                r_parent.link_left(r_left)
                r_parent.link_predecessor(r_left.getMax())
        else:
            replacement.link_left(r_left)
            replacement.link_predecessor(r_left.getMax())
    del z
    #collapse when two nodes are the same
    if replacement and replacement.successor and replacement.value == replacement.successor.value:
        tree.delete(replacement.successor)
    elif replacement and replacement.predecessor and replacement.value == replacement.predecessor.value:
        tree.delete(replacement.predecessor)



#--------------------
# def UTILITY DIRECTION OBJECTS:
#--------------------
class Direction(object):
    def __init__(self):
        return
    def __str__(self):
        return "Direction"
class Left(Direction):
    def __init__(self):
        return
    def __str__(self):
        return "Left"
class Right(Direction):
    def __init__(self):
        return
    def __str__(self):
        return "Right"
class Centre(Direction):
    def __init__(self):
        return
    def __str__(self):
        return "Centre"


