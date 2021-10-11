from .attack import Attack
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships
from ...announcement import Announcement as Ann



class SubprefixHijack(Attack):
    __slots__ = ["victim_prefix", "attacker_prefix"]
    def __init__(self, attacker=ASNs.ATTACKER.value, victim=ASNs.VICTIM.value):

        self.victim_prefix = Prefixes.PREFIX.value
        self.attacker_prefix = Prefixes.SUBPREFIX.value

        anns = [self.AnnCls(prefix=self.victim_prefix,
                    timestamp=Timestamps.VICTIM.value,
                    as_path=(victim,),
                    seed_asn=victim,
                    roa_validity=ROAValidity.VALID,
                    recv_relationship=Relationships.ORIGIN,
                    withdraw=False,
                    traceback_end=False),
                self.AnnCls(prefix=self.attacker_prefix,
                    timestamp=Timestamps.ATTACKER.value,
                    as_path=(attacker,),
                    seed_asn=attacker,
                    roa_validity=ROAValidity.INVALID,
                    recv_relationship=Relationships.ORIGIN,
                    withdraw=False,
                    traceback_end=False)]
        super(SubprefixHijack, self).__init__(attacker, victim, anns)
