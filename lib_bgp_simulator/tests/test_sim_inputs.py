from dataclasses import dataclass
import itertools

import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships, ROAValidity
from ..announcements import AnnWDefaults

from ..engine import BGPAS
from ..engine import BGPRIBsAS
from ..engine import LocalRib
from ..engine_input import EngineInput

from ..simulator import Graph
from ..simulator import MPMethod
from ..simulator import Simulator


@pytest.mark.slow
@pytest.mark.parametrize("AdoptASCls, EngineInputCls, num_trials, "
                         "BaseASCls, mp_method",
                         itertools.product(*[BGPAS.subclasses,
                                             EngineInput.subclasses,
                                             # Just one trials tests no stdev
                                             # Two trials tests stdev
                                             [1, 2],
                                             BGPAS.subclasses,
                                             [MPMethod.SINGLE_PROCESS, MPMethod.MP]]))
def test_sim_inputs(AdoptASCls,
                    EngineInputCls,
                    num_trials,
                    BaseASCls,
                    mp_method,
                    tmp_path):
    """Test basic functionality of process_incoming_anns"""

    tmp_dir = tmp_path / "test_sim_inputs"
    tmp_dir.mkdir()

    sim = Simulator(_dir=str(tmp_dir))
    graph = Graph(percent_adoptions=[0, 50, 100],
                  adopt_as_classes=[AdoptASCls],
                  EngineInputCls=EngineInputCls,
                  num_trials=num_trials,
                  BaseASCls=BaseASCls)
    sim.run(graphs=[graph],
            graph_path=tmp_dir / "graphs.tar.gz",
            mp_method=mp_method)
