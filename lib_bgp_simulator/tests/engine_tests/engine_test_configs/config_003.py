from ..graphs import Graph002
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config003(EngineTestConfig):
    """Contains config options to run a test"""

    name = "003"
    desc = "Basic BGP Propagation (with simple AS)"
    scenario = ValidPrefix(victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=BGPSimpleAS)
    graph = Graph002()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
