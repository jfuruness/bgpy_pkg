from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph002
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config003(EngineTestConfig):
    """Contains config options to run a test"""

    name = "003"
    desc = "Basic BGP Propagation (with simple AS)"
    scenario = ValidPrefix(
        victim_asns={ASNs.VICTIM.value}, AdoptASCls=None, BaseASCls=BGPSimpleAS
    )
    graph = Graph002()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
