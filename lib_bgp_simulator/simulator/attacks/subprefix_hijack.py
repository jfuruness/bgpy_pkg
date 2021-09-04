from .attack import Attack
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity
from ...announcement import Announcement as Ann



class SubprefixHijack(Attack):
    __slots__ = []
    def __init__(self, attacker=ASNs.ATTACKER.value, victim=ASNs.VICTIM.value):
        anns = [Ann(prefix=Prefixes.PREFIX.value,
                    timestamp=Timestamps.VICTIM.value,
                    as_path=(victim,),
                    seed_asn=victim,
                    roa_validity=ROAValidity.VALID),
                Ann(prefix=Prefixes.SUBPREFIX.value,
                    timestamp=Timestamps.ATTACKER.value,
                    as_path=(attacker,),
                    seed_asn=attacker,
                    roa_validity=ROAValidity.INVALID)]
        super(SubprefixHijack, self).__init__(attacker, victim, anns)
