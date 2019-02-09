import logging as root_logger
from .operatorTemplate import OperatorTemplate
from .City import verify_results
from cairo_utils.dcel.constants import VertE
import IPython
logging = root_logger.getLogger(__name__)
class IntersectionOperator(OperatorTemplate):
    """ Operator to create an intersection """

    def __init__(self):
        super().__init__()


    def verify(self, delta):
        """ Performs the operator, returns all changes as a list """

        #run the intersection algorithm
        roadSet = set([x for x in self.dc.halfEdges if "road" in x.data])
        logging.info("Road Set: {}".format(len(roadSet)))
        intersections = self.dc.intersect_halfEdges(edgeSet=roadSet)
        if bool(intersections):
            for i in intersections:
                i.vertex.data[VertE.RADIUS] = 40
                i.vertex.data["intersection"] = True
        #create intersections for roads



        return (verify_results.PASS, [])

    def is_oneshot(self):
        return False

    def unwind(self):
        return
