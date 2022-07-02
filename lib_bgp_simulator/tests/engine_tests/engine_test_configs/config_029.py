from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....engine import BGPSimpleAS
from ....enums import ASNs, Prefixes, Timestamps, Relationships
from ....scenarios import MultiValidPrefix


class Custom29MultiValidPrefix(MultiValidPrefix):
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
            if victim_asn == 5:
                # longer path to test path length preference
                vic_anns[-1].as_path = (victim_asn, victim_asn)
        return vic_anns


class Config029(EngineTestConfig):
    """Contains config options to run a test"""

    name = "029"
    desc = "Test of path length preference"
    scenario = Custom29MultiValidPrefix(
        attacker_asn=ASNs.ATTACKER.value,
        victim_asn=3,  # the correct destination
        victim_asns=[3, 5],
        AdoptASCls=None,
        BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1

