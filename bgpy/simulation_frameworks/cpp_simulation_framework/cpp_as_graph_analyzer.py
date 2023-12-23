from typing import Union

from bgpy.bgpc import CPPSimulationEngine

from bgpy.enums import CPPOutcomes, PyOutcomes
from bgpy.simulation_frameworks.base import ASGraphAnalyzer

from bgpy.simulation_frameworks.py_simulation_framework.scenarios import Scenario


class CPPASGraphAnalyzer(ASGraphAnalyzer):
    """Takes in a SimulationEngine and outputs metrics"""

    def __init__(self, engine: CPPSimulationEngine, scenario: Scenario):
        self.engine: CPPSimulationEngine = engine
        assert isinstance(self.engine, CPPSimulationEngine), "C++ will explode"
        self.scenario: Scenario = scenario

        self._cpp_as_graph_analyzer = CPPASGraphAnalyzer(
            self.engine,
            list(self.scenario.ordered_prefix_subprefix_dict),
            self.scenario.victim_asns,
            self.scenario.attacker_asns,
        )

    def analyze(self) -> dict[int, dict[int, Union["CPPOutcomes", "PyOutcomes"]]]:
        """Takes in engine and outputs traceback for ctrl + data plane data"""

        return self._cpp_as_graph_analyzer.analyze()
