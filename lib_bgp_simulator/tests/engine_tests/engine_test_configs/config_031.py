from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....engine import BGPSimpleAS
from ....enums import ASNs, Prefixes, Timestamps, Relationships
from ....scenarios import ValidPrefix


class Custom31ValidPrefix(ValidPrefix):
    """A valid prefix engine input"""

    __slots__ = ()

    def _get_announcements(self):
        """Returns a valid prefix announcement

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """
        vic_ann = self.AnnCls(prefix=Prefixes.PREFIX.value,
                              as_path=(self.victim_asn, 1, self.victim_asn),
                              timestamp=Timestamps.VICTIM.value,
                              seed_asn=self.victim_asn,
                              roa_valid_length=True,
                              roa_origin=self.victim_asn,
                              recv_relationship=Relationships.ORIGIN)
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

