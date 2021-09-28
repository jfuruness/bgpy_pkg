from .attack import Attack
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships
from ...announcement import Announcement as Ann


class UnannouncedPrefixHijack(Attack):
    __slots__ = ["victim_prefix", "attacker_prefix"]
    def __init__(self, attacker=ASNs.ATTACKER.value, victim=None):
        self.victim_prefix = None
        self.attacker_prefix = prefix=Prefixes.PREFIX.value

        anns = [self.AnnCls(prefix=self.attacker_prefix,
                    timestamp=Timestamps.ATTACKER.value,
                    as_path=(attacker,),
                    seed_asn=attacker,
                    roa_validity=ROAValidity.INVALID,
                    recv_relationship=Relationships.ORIGIN)]
        super(UnannouncedPrefixHijack, self).__init__(attacker, None, anns)
