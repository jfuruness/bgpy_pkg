import pytest

from bgpy.caida_collector import CaidaCollector

from ....simulation_engine import BGPSimpleAS
from ....simulation_engine import SimulationEngine


@pytest.fixture(scope="session")
def engine():
    # Engine is not picklable or dillable AT ALL, so do it here
    # (after the multiprocess process has started)
    # Changing recursion depth does nothing
    # Making nothing a reference does nothing
    return CaidaCollector(
        BaseASCls=BGPSimpleAS,
        GraphCls=SimulationEngine,
    ).run(tsv_path=None)
