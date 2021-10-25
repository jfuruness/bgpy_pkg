from dataclasses import dataclass
import itertools

import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ...enums import ASNs, Relationships, ROAValidity
from ...announcements import AnnWDefaults

from ...engine import BGPSimpleAS
from ...engine import BGPAS
from ...engine import LocalRIB
from ...engine_input import EngineInput

from ...simulator import Graph
from ...simulator import MPMethod
from ...simulator import Simulator


# Really does need all these combos
# Since certain as classes might break with mp
@pytest.mark.slow
@pytest.mark.parametrize("AdoptASCls, EngineInputCls, mp_method",
                         itertools.product(*[BGPSimpleAS.as_classes,
                                             EngineInput.subclasses,
                                             [MPMethod.SINGLE_PROCESS, MPMethod.MP]]))
def test_sim_inputs(AdoptASCls,
                    EngineInputCls,
                    mp_method,
                    tmp_path):
    """Test basic functionality of process_incoming_anns"""

    tmp_dir = tmp_path / "test_sim_inputs"
    tmp_dir.mkdir()

    sim = Simulator(_dir=str(tmp_dir),
                    parse_cpus=2)
    graph = Graph(percent_adoptions=[0, 50, 100],
                  adopt_as_classes=[AdoptASCls],
                  EngineInputCls=EngineInputCls,
                  num_trials=1,
                  # No need to modify BaseASCls
                  # Because we test every possibility of AdoptASCls
                  # We actually test all combos of base - adopt class
                  BaseASCls=BGPSimpleAS)
    sim.run(graphs=[graph],
            graph_path=tmp_dir / "graphs.tar.gz",
            mp_method=mp_method)
