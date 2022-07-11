
def create_test_config(graph, name, comment):
    test_template = """
from ..graphs import {graph}
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import SubprefixHijack


class Config{name}(EngineTestConfig):
    {comment}
    name = "{name}"
    desc = "BGP hidden hijack (with simple AS)"
    scenario = SubprefixHijack(attacker_asn=ASNs.ATTACKER.value,
                                victim_asn=ASNs.VICTIM.value,
                                AdoptASCls=None,
                                BaseASCls=BGPSimpleAS)
    graph = {graph}()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
""".format(graph=graph, name=name, comment=comment)
    return test_template
