from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....engine import BGPSimpleAS
from ....enums import ASNs, Prefixes, Timestamps, Relationships
from ....scenarios import ValidPrefix


class Custom31ValidPrefix(ValidPrefix):
    """A valid prefix engine input"""

    __slots__ = ()

    def _get_announcements(self):
        vic_ann = super()._get_announcements()[0]
        # Add 1 to the path so AS 1 rejects this
        vic_ann.as_path = (self.victim_asn, 1, self.victim_asn)
        return (vic_ann,)


class Config031(EngineTestConfig):
    """Contains config options to run a test"""

    name = "031"
    desc = "Test loop prevention mechanism"
    scenario = Custom31ValidPrefix(
        attacker_asn=ASNs.ATTACKER.value,
        victim_asn=4,
        AdoptASCls=None,
        BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1

