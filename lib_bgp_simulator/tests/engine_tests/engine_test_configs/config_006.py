from ..graphs import Graph002
from ..utils import EngineTestConfig

from ....engine import ROVAS
from ....enums import ASNs
from ....scenarios import ValidPrefix


class Config006(EngineTestConfig):
    """Contains config options to run a test"""

    name = "006"
    desc = "Basic BGP Propagation (with ROV AS)"
    scenario = ValidPrefix(victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=ROVAS)
    graph = Graph002()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
