from ..graphs import Graph002
from ..utils import EngineTestConfig

from ....engine import ROVSimpleAS
from ....enums import ASNs
from ....scenarios import ValidPrefix


class Config005(EngineTestConfig):
    """Contains config options to run a test"""

    name = "005"
    desc = "Basic BGP Propagation (with ROV Simple AS)"
    scenario = ValidPrefix(victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=ROVSimpleAS)
    graph = Graph002()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
