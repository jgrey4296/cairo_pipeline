
from enum import Enum
from random import choice
import logging as root_logger
import IPython
from .operatorTemplate import OperatorTemplate

logging = root_logger.getLogger(__name__)

verify_results = Enum("Verify Results", "PASS FAIL SANCTION")

class City:
    """
    A City Class to Relate the DCEL
    to city requirements
    """

    def __init__(self, standard_rules=None, specific_rules=None):
        #Verification rules can be looked up,
        #passed in, or always applied
        assert(standard_rules is None or isinstance(standard_rules, list))
        assert(specific_rules is None or isinstance(specific_rules, dict))
        #TODO: verify all rules possess a verify method
        self.standard_rules = []
        self.specific_rules = {}

        self.actors = {}
        self.current_actor = None

        if standard_rules is not None:
            self.standard_rules = standard_rules
        if specific_rules is not None:
            self.specific_rules.update(specific_rules)

    def choose_operator(self, operators):
        op = choice(operators)
        return op

    def verify(self, dc, i, delta, verify_type=None):
        logging.info("Verifying Latest Operator Tick")
        #Verify the dcel
        #where delta is the changes made this timestep
        result = (verify_results.PASS, [])
        for r in self.standard_rules:
            #apply the rule
            #result = self.updateResult(r(dc, delta))
            continue
        if verify_type is not None and verify_type in self.specific_rules:
            for r in self.specific_rules[verify_type]:
                with OperatorTemplate.setup_operator(r, dc, i, city=self):
                    result = self.updateResult(result, r.verify(delta))



        #update the city state with a sanction
        self.sanction(result[1])

        return result[0]

    def updateResult(self, curResult, newResult):
        if newResult[0] is not verify_results.PASS:
            return (newResult[0], curResult[1] + newResult[1])
        return curResult

    def sanction(self,sanctionInfo):
        assert(isinstance(sanctionInfo, list))
        if not bool(sanctionInfo):
            return
        logging.info("Sanctioning Actor: {}".format(self.current_actor))
