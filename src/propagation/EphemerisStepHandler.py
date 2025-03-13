from typing import List

from org.orekit.propagation import SpacecraftState
from org.orekit.propagation.sampling import PythonOrekitFixedStepHandler
from org.orekit.time import AbsoluteDate


class EphemerisStepHandler(PythonOrekitFixedStepHandler):
    def __init__(self):
        super(EphemerisStepHandler,self).__init__()
        self.states:List[SpacecraftState] = []

    def init(self, initial_state:SpacecraftState, t:AbsoluteDate, step: float):
        pass

    def handleStep(self, current_state:SpacecraftState):
        self.states.append(current_state)

    def finish(self, final_state: SpacecraftState):
        pass