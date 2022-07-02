from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....engine import BGPSimpleAS
from ....enums import ASNs, Prefixes, Timestamps, Relationships
from ....scenarios import MultiValidPrefix


class Custom30MultiValidPrefix(MultiValidPrefix):
    """A valid prefix engine input with multiple victims"""

    __slots__ = ()

    def _get_announcements(self):
        """Returns several valid prefix announcements"""
        if self.victim_asns is None:
            return None
        vic_anns = []
        for victim_asn in self.victim_asns:
            vic_anns.append(self.AnnCls(
                prefix=Prefixes.PREFIX.value,
                as_path=(victim_asn,),
                timestamp=Timestamps.VICTIM.value,
                seed_asn=victim_asn,
                roa_valid_length=True,
                roa_origin=victim_asn,
                recv_relationship=Relationships.ORIGIN))
            if victim_asn == 1:
                # longer path
                vic_anns[-1].as_path = (1, 1, 1)
        return vic_anns


class Config030(EngineTestConfig):
    """Contains config options to run a test"""

    name = "030"
    desc = "Test seeded announcement should never be replaced"
    scenario = Custom30MultiValidPrefix(
        attacker_asn=ASNs.ATTACKER.value,
        victim_asn=4,  # the correct destination
        victim_asns=[1, 4, 3, 5],
        AdoptASCls=None,
        BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1

