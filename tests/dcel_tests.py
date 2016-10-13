import unittest
from beachlinecontext import dcel
from dcel import Vertex,Line,HalfEdge,Face,DCEL
import IPython

class DCEL_tests(unittest.TestCase):

    def test_Line_Creation(self):
        va = Vertex(1,1)
        vb = Vertex(3,1)
        line = Line.newLine(va,vb)
        self.assertEqual(line.source.x,1)
        self.assertEqual(line.source.y,1)
        self.assertEqual(line.direction.x,1)
        self.assertEqual(line.direction.y,0)
        self.assertEqual(line.length,2)
        destination = line.destination()
        self.assertEqual(destination.x,vb.x)
        self.assertEqual(destination.y,vb.y)

    def test_constraint(self):
        line = Line.newLine(Vertex(-2,-4),Vertex(5,4))
        dest1 = line.destination()
        self.assertEqual(dest1.x,5)
        self.assertEqual(dest1.y,4)
        line.constrain(-1,-5,4,5)
        self.assertEqual(line.source.x,-1)
        self.assertEqual(line.source.y,-4)
        destination = line.destination()
        self.assertEqual(destination.x,4)
        self.assertEqual(destination.y,4)
        
        
    


if __name__ == "__main__":
    unittest.main()
