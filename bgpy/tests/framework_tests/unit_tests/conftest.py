import pytest

from bgpy.caida_collector import CaidaCollector, AS

from ....simulation_engine import BGPSimplePolicy
from ....simulation_engine import SimulationEngine


@pytest.fixture(scope="session")
def engine():
    # Engine is not picklable or dillable AT ALL, so do it here
    # (after the multiprocess process has started)
    # Changing recursion depth does nothing
    # Making nothing a reference does nothing
    return CaidaCollector(
        BasePolicyCls=BGPSimplePolicy,
        BaseASCls=AS,
        GraphCls=SimulationEngine,
    ).run(tsv_path=None)
