from enum import Enum
import IPython
import logging as root_logger
from cairo_utils.math import getRanges
logging = root_logger.getLogger(__name__)


class OperatorTemplate:
    """
    A Template Class for Creating an individual operator on the city generator
    """

    def __init__(self):
        self.delta = []
        return

    @staticmethod
    def setup_operator(op, dc, i, city=None):
        assert(isinstance(op, OperatorTemplate))
        op.dc = dc
        op.i = i
        op.city = city
        return op

    def operate(self, draw=True, override=False):
        """ Performs the operator, returns all changes as a list """
        self.delta = []
        #if necessary to exit early:
        #return delta

        if not draw:
            return self.delta

        return self.delta

    def __enter__(self):
        """ Enters the context for op parameterization """
        return

    def __exit__(self, type, value, traceback):
        """ Exits, and can unwind the operator """
        if type is not None and type(value) is not None:
            logging.warning("Operator Failed, rewinding")
            self.unwind()

        self.dc = None
        self.i = None
        self.delta = []

    def is_oneshot(self):
        return False

    def unwind(self):
        raise Exception("Unwind: Unimplemented")

    def __call__(self, draw=False, override=False):
        raise Exception("Call: Unimplemented")


    def setup_values(self, bbox):
        """ Get the lengths, widths and deviance values, from
        a passed in bbox """
        maxmin = getRanges(bbox.reshape((2,2)))
        ranges = maxmin[:,1] - maxmin[:,0]
        mid_ways = (ranges * 0.5).astype(int)
        return (maxmin, ranges, mid_ways)
