## A Red-Black Tree bastardisation into a Beach Line for fortune's
# Properties of RBTrees:
# 1) Every node is Red Or Black
# 2) The root is black
# 3) Every leaf is Black, leaves are null nodes
# 4) If a node is red, it's children are black
# 5) All paths from a node to its leaves contain the same number of black nodes

from string import ascii_uppercase
import IPython

#--------------------
#def Beachline Container
#--------------------
class BeachLine(object):

    def __init__(self,arc=True):
        """ Initialise the rb tree container, ie: the node list """
        self.arc = arc
        self.nodes = []
        self.arcs_added = []
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
        lst = [str(x) for x in self.get_chain()]
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
            if type(direction) is Right:
                self.insert_successor(node,value)
            elif type(direction) is Left:
                self.insert_predecessor(node,value)
            else:
                raise Exception("search returned an exact match")
        
    def insert_successor(self,existing_node,newValue):
        self.arcs_added.append(newValue)
        new_node = Node(newValue,arc=self.arc)
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
        if existing_node is None:
            existing_node = self.root
        if existing_node is None:
            self.root = new_node
        else:
            existing_node.add_left(new_node)
        self.balance(new_node)
        return new_node
    
    # def delete(self,z):
    #     """ Delete a leaf, collapsing parents as necessary,  """
    #     try:
    #         print("Deleting Leaf: ",ascii_uppercase[z.value.id], z.arc)
    #     except Exception as e:
    #         print("Deleting Leaf with value: ",z.value)
    #     node_parent = z.parent
    #     #Base case: Root
    #     if node_parent is None and self.root == z:
    #         self.root = None
    #         return
    #     #General Case:        
    #     #transplant the opposite side to the parent
    #     if node_parent.left == z:
    #         transplant(self,node_parent,node_parent.right)
    #     else:
    #         transplant(self,node_parent,node_parent.left)
    #     #collapse if two arcs are of the same parabola:
    #     node_grand_parent = node_parent.parent
    #     while node_grand_parent is not None:
    #         node_parent = node_grand_parent.parent
    #         node_grand_parent = self.collapse_duplicate_arcs(node_grand_parent)
    #     #rebalance
    #     if node_parent:
    #         rbDeleteFixup(self,node_parent)

    def delete(self,node):
        """ Delete a value from the tree """
        rbTreeDelete(self,node)

    def search(self,x,d=None):
        """ Search the tree for a value, getting closest node to it, 
            returns (node,insertion_function)
        """
        current = self.root
        if current is None:
            return None #not found
        parent = None
        found = False
        insertPre = False
        while not found:
            comp = current.compare(x,d=d,arc=self.arc)
            if type(comp) is Left:
                parent = current
                current = current.left
            elif type(comp) is Right:
                parent = current
                current = current.right
            elif comp is None or type(comp) is Centre:
                #ie: spot on
                parent = current
                found = True
            if current is None:
                found = True
                
        return (parent, comp) #the existing parent and the side to add it
        
    def min(self):
        """ Get the min value of the tree """
        return self.root.getMin()

    def max(self):
        """ Get the max value of the tree """
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
            chain.append(current)
            current = current.successor
        return [x.value for x in chain]

    def collapse_adjacent_arcs(self,node):
        """ If a node has the same arc as a successor/predecessor,
            just collapse them together, deleting one node
        """
            
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

    def compare(self,x,d=None,arc=True):
        """ given an x coord, return whether the point intersects on the left, in the middle, or on the right of the arc and its successor/predecessor """
        if arc: #compare arcs
            print("Arc Testing")
        else: # compare straight values:
            if x < self.value:
                return Left()
            elif x > self.value:
                return Right()
            else:
                return Centre()
        

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
        
    def isSingleArc(self):
        return True

    def isLeaf(self):
        return self.left == None and self.right == None
    
    def intersect(self,node):
        raise Exception("Not implemented yet: intersect")

    def update_arcs(self,d):
        if self.arc:
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
        if self.isSingleArc():
            return ascii_uppercase[self.arc.id]
        else:
            a = None
            b = None
            if self.left:
                a = self.left.print_parabola_id()
            if self.right:
                b = self.right.print_parabola_id()
            return "( {} {} )".format(a,b)

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
        return self.getMin().arc

    def getMaxArc(self):
        return self.getMax().arc

    
    def add_left(self,node,force=False):
        prev = self.predecessor
        if self.left is None or force:
            self.left = node
            if self.left is not None:
                self.left.predecessor = prev
                self.left.successor = self
                self.left.parent = self
            if prev:
                prev.successor = self.left
            self.predecessor = node
        else:
            left_max = self.left.getMax()
            if left_max != prev:
                raise Exception("left_max is not prev")
            left_max.add_right(node)
        
    def add_right(self,node,force=False):
        succ = self.successor
        if self.right is None or force:
            self.right = node
            if self.right is not None:
                self.right.predecessor = self
                self.right.successor = succ
                self.right.parent = self
            if succ:
                succ.predecessor = self.right
            self.successor = node
        else:
            right_min = self.right.getMin()
            if right_min != succ:
                raise Exception("Right_min is not succ")
            right_min.add_left(node)
        
        
#--------------------
# def Helper functions
#--------------------

def rotateLeft(tree,node):
    """ Rotate the given node left, making the new head be node.right """
    if node is None or node.right is None:
        raise Exception("Rotating left when there is no right")
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
        tree.root = newHead
    elif node == originalParent.left:  #update the parent's left subtree
        originalParent.left = newHead
        newHead.parent = originalParent
    else:
        originalParent.right = newHead
        newHead.parent = originalParent

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
        tree.root = newHead
    elif node == originalParent.left:
        originalParent.left = newHead
        newHead.parent = originalParent
    else:
        originalParent.right = newHead
        newHead.parent = originalParent

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
    elif u == u.parent.left:
        u.parent.add_left(v,force=True)
    else:
        u.parent.add_right(v,force=True)


def rbTreeDelete(tree,z):
    parent = z.parent
    predecessor = z.predecessor
    successor = z.successor
    left = z.left
    right = z.right
    replacement = None
    sideLeft = False
    
    if successor is not None:
        replacement = successor
        #delink the replacement's parent
        if replacement.parent.left == replacement:
            replacement.parent.left = None
            replacement.parent = None
        else:
            replacement.parent.right = None
            replacement.parent = None
        #link z's predecessor to replacement
        if predecessor is not None:
            predecessor.successor = replacement
            replacement.predecessor = predecessor
        else:
            replacement.predecessor = None
        #link the replacement to the original parent
        if parent is not None:
            if parent.right == z:
                parent.right = replacement
                replacement.parent = parent
            else:
                parent.left = replacement
                replacement.parent = parent
        else:
            tree.root = replacement
        #link the replacement to the right of the old node:
        if right != replacement:
            replacement.right = right
            right.parent = replacement
        #link left:
        if left is not None:
            replacement.left = left
            left.parent = replacement
        
    else: #no successor:
        replacement = predecessor
        #delink the replacement's parent
        if replacement.parent.left == replacement:
            replacement.parent.left = None
            replacement.parent = None
        else:
            replacement.parent.right = None
            replacement.parent = None
        replacement.successor = None
        if parent is not None:
            if parent.right == z:
                parent.right = replacement
                replacement.parent = parent
            else:
                parent.left = replacement
                replacement.parent = parent
        else:
            tree.root = replacement
        #no link right, as no successor
        #link left
        if left is not None:
            replacement.left = left
            left.parent = replacement
    del z
    
 
def rbDeleteFixup(tree,x):
    """ After deleting a node, verify the RB properties hold """
    while x is not None and x != tree.root and not x.red: #keep going till you hit the root
        if x == x.parent.left: #Operate on the left subtree
            w = x.parent.right 
            if w.red: # opposite subtree is red
                w.red = False #switch colour of that tree and parent
                x.parent.red = True
                rotateLeft(tree,x.parent) #then rotate
                w = x.parent.right #update the the opposite subtree to the new subtree
            if (w.left is None or not w.left.red) and (w.right is None or not w.right.red): #if both subtrees are black
                w.red = True #recolour the subtree head
                x = x.parent #and move up
            else: #different colours on the subtrees
                if not w.right.red:
                    w.left.red = False #normalise the colours of the left and right
                    w.red = True #flip the parent colour
                    rotateRight(tree,w) #rotate
                    w = x.parent.right #update the subtree focus
                if x.parent is not None:
                    w.red = x.parent.red 
                    x.parent.red = False
                if w.right is not None:
                    w.right.red = False
                rotateLeft(tree,x.parent) #rotate back if necessary
                x = tree.root 
        else: #mirror image for right subtree
            w = x.parent.left
            if w.red:
                w.red = False
                x.parent.red = True
                rotateRight(tree,x.parent)
                w = x.parent.left
            if w is None:
                continue
            if (w.right is None or not w.right.red) and (w.left is None or not w.left.red):
                w.red = True
                x = x.parent
            elif not w.left.red:
                w.right.red = False
                w.red = True
                rotateLeft(tree,w)
                w = x.parent.left
            if x.parent is not None:
                w.red = x.parent.red
                x.parent.red = False
            if w.left is not None:
                w.left.red = False
            rotateRight(tree,x.parent)
            x = tree.root
    if x is not None:
        x.red = False
            


#--------------------
# def UTILITY DIRECTION OBJECTS:
#--------------------
class Direction(object):
    def __init__(self):
        return
class Left(Direction):
    def __init__(self):
        return
class Right(Direction):
    def __init__(self):
        return
class Centre(Direction):
    def __init__(self):
        return


