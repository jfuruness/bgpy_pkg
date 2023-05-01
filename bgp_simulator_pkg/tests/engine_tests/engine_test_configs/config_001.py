from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph001
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import SubprefixHijack


class Config001(EngineTestConfig):
    """Contains config options to run a test"""

    name = "001"
    desc = "BGP hidden hijack (with simple AS)"
    scenario = SubprefixHijack(
        attacker_asns={ASNs.ATTACKER.value},
        victim_asns={ASNs.VICTIM.value},
        BaseASCls=BGPSimpleAS,
    )
    graph = Graph001()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
