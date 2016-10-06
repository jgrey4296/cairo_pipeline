import unittest
from beachlinecontext import beachline
from beachline import BeachLine, Node, Centre, Left, Right
import logging

class BeachLineTests(unittest.TestCase):
    """ Tests for Simple Valued Beachlines (not arc-based) """

    def setUp(self):
        self.b = BeachLine(arc=False)

    def tearDown(self):
        del self.b
        
    def test_init(self):
        """ Check initial creation """
        self.assertIsInstance(self.b,BeachLine)
        self.assertFalse(self.b.arc)
        self.assertIsNone(self.b.root)
        self.assertEqual(len(self.b.nodes),0)
        self.assertEqual(len(self.b.arcs_added),0)

    def test_isEmptyOnInit(self):
        """ Check the beachline is empty on initial creation """
        self.assertTrue(self.b.isEmpty())
        self.assertEqual(len(self.b.get_chain()),0)

    def test_minmax_on_empty_beachline(self):
        """ Check that min and max respond appropriately on an empty beachline """
        #todo: make these raise exceptions
        self.assertIsNone(self.b.min())
        self.assertIsNone(self.b.max())

class TestNodeCreation(unittest.TestCase):

    def setUp(self):
        self.value = 5
        self.node = Node(self.value,arc=False)

    def tearDown(self):
        del self.node

    def test_init(self):
        """ Check initial node creation """
        self.assertIsInstance(self.node,Node)
        self.assertTrue(self.node.red)
        self.assertEqual(self.node.value,self.value)
        self.assertIsNone(self.node.left_circle_event)
        self.assertIsNone(self.node.right_circle_event)
        self.assertIsNone(self.node.left)
        self.assertIsNone(self.node.right)
        self.assertIsNone(self.node.parent)
        self.assertIsNone(self.node.successor)
        self.assertIsNone(self.node.predecessor)
        self.assertEqual(str(self.node),str(self.value))
        self.assertFalse(self.node.arc)
        self.assertTrue(self.node.isLeaf())

    def test_getMin_on_leaf(self):
        """ Check getmin will get itself when called on leaf """
        self.assertEqual(self.node,self.node.getMin())

    def test_getMax_on_leaf(self):
        """ check getmax wil get itself when called on leaf """
        self.assertEqual(self.node,self.node.getMax())

    def test_getMaxValue_on_leaf(self):
        """ check getting maxvalue on a leaf will return the nodes value """
        self.assertEqual(self.node.value,self.node.getMaxValue())

    def test_getMinValue_on_leaf(self):
        """ check getting the minvalue on a leaf will return the nodes value """
        self.assertEqual(self.node.value,self.node.getMinValue())

    def test_compare_simple(self):
        """ check comparison works on simple value """
        self.assertIsInstance(self.node.compare_simple(self.value),Centre)
        self.assertIsInstance(self.node.compare_simple(self.value - 2),Left)
        self.assertIsInstance(self.node.compare_simple(self.value + 2),Right)
        
    def test_compare_for_non_arcs(self):
        """ check compare calls compare_simple correctly for simple values """ 
        self.assertIsInstance(self.node.compare(self.value),Centre)
        self.assertIsInstance(self.node.compare(self.value - 2),Left)
        self.assertIsInstance(self.node.compare(self.value + 2),Right)
        
        
class TrivialInsertBeachLineTestCase(unittest.TestCase):

    def setUp(self):
        self.b = BeachLine(arc=False)
        self.testvalue = 5
        self.b.insert(self.testvalue)

    def tearDown(self):
        del self.b

    def test_insert_singular(self):
        """ Test insertion works on a trivial case """
        self.assertFalse(self.b.isEmpty())
        self.assertIsInstance(self.b.root,Node)
        self.assertEqual(self.b.root.value,self.testvalue)
        self.assertEqual(len(self.b.nodes),1)
        self.assertEqual(len(self.b.arcs_added),1)

    def test_trivial_search(self):
        """ Check trivial root only search works """
        node,side = self.b.search(self.testvalue)
        self.assertIsInstance(node,Node)
        self.assertIsInstance(side,Centre)
        self.assertEqual(self.b.root,node)
        self.assertEqual(self.b.root,self.b.nodes[0])

    def test_root_is_black(self):
        """ Assert that the root is changed from red to black correctly """
        self.assertFalse(self.b.root.red)
        
    def test_empty_successor_and_predecessor(self):
        """ Check the successor/predecessor are empty in the trivial case """
        node,side = self.b.search(self.testvalue)
        self.assertIsNone(node.predecessor)
        self.assertIsNone(node.successor)


class ExpandedInsertion_tests(unittest.TestCase):

    def setUp(self):
        self.original_test_value = 5
        self.b = BeachLine(arc=False)
        self.b.insert(self.original_test_value)
        
    def tearDown(self):
        del self.b

    def test_greater_insert(self):
        greaterValue = self.original_test_value + 10
        self.b.insert(greaterValue)
        self.assertEqual(len(self.b.nodes),2)
        self.assertEqual(len(self.b.arcs_added),2)
        self.assertEqual(self.b.root.value,self.original_test_value)
        #check the value is inserted on the right, and is the successor:
        self.assertIsInstance(self.b.root.right,Node)
        self.assertFalse(self.b.root.isLeaf())
        self.assertTrue(self.b.root.right.isLeaf())
        self.assertEqual(self.b.root.successor,self.b.root.right)
        self.assertEqual(self.b.nodes[1],self.b.root.successor)
        self.assertEqual(self.b.root.right.value,greaterValue)
        #check parentage
        self.assertEqual(self.b.root.right.parent,self.b.root)
        self.assertEqual(self.b.root.right.predecessor,self.b.root)

    def test_lesser_insert(self):
        lesserValue = self.original_test_value - 10
        self.b.insert(lesserValue)
        self.assertEqual(len(self.b.nodes),2)
        self.assertEqual(len(self.b.arcs_added),2)
        self.assertEqual(self.b.root.value,self.original_test_value)
        #now check the value is inserted on the left, and is the predecessor
        self.assertIsInstance(self.b.root.left,Node)
        self.assertFalse(self.b.root.isLeaf())
        self.assertTrue(self.b.root.left.isLeaf())
        self.assertEqual(self.b.root.predecessor,self.b.root.left)
        self.assertEqual(self.b.root.left.successor,self.b.root)
        self.assertEqual(self.b.nodes[1],self.b.root.left)
        self.assertEqual(self.b.nodes[1].value,lesserValue)
        self.assertEqual(self.b.root.left.parent,self.b.root)

    def test_triple_insertions(self):
        lesserValue = self.original_test_value - 10
        greaterValue = self.original_test_value + 10
        self.b.insert(lesserValue)
        self.b.insert(greaterValue)
        self.assertEqual(len(self.b.nodes),3)
        self.assertEqual(self.b.root.left.value,lesserValue)
        self.assertEqual(self.b.root.right.value,greaterValue)
        self.assertEqual(self.b.root.value,self.original_test_value)
        

class SimpleBeachLine_Deletion_tests(unittest.TestCase):

    def setUp(self):
        self.b = BeachLine(arc=False)

    def tearDown(self):
        del self.b

    def test_deletion(self):
        value = 10
        self.b.insert(10)
        self.assertIsInstance(self.b.root,Node)
        self.assertEqual(len(self.b.nodes),1)
        self.b.delete_value(value)
        self.assertEqual(len(self.b.nodes),0)
        self.assertIsNone(self.b.root)

    def test_multi_insert_then_delete_leaf(self):
        value1 = 10
        value2 = value1 + 10
        self.b.insert(value1)
        self.b.insert(value2)
        self.assertEqual(len(self.b.nodes),2)
        self.assertIsInstance(self.b.root.right,Node)
        
        self.b.delete_value(value2)

        self.assertEqual(len(self.b.nodes),1)
        self.assertIsNone(self.b.root.right)

    

        
if __name__ == '__main__':
    unittest.main()

#self.assertEqual("foo".upper(),'FOO')
