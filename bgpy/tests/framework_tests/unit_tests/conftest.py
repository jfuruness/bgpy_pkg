import pytest

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.simulation_engine import SimulationEngine


@pytest.fixture(scope="session")
def engine() -> SimulationEngine:
    # Engine is not picklable or dillable AT ALL, so do it here
    # (after the multiprocess process has started)
    # Changing recursion depth does nothing
    # Making nothing a reference does nothing
    as_graph = CAIDAASGraphConstructor().run()
    return SimulationEngine(as_graph)
