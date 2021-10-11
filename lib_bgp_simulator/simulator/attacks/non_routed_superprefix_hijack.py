from .attack import Attack
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships
from ...announcement import Announcement as Ann


class NonRoutedSuperprefixHijack(Attack):
    __slots__ = []
    def __init__(self, attacker=ASNs.ATTACKER.value, victim=ASNs.VICTIM.value):
        anns = [self.AnnCls(prefix=Prefixes.SUPERPREFIX.value,
                            timestamp=Timestamps.ATTACKER.value,
                            as_path=(attacker,),
                            seed_asn=attacker,
                            roa_validity=ROAValidity.UNKNOWN,
                            recv_relationship=Relationships.ORIGIN,
                            withdraw=False,
                            traceback_end=False)]
        super(NonRoutedSuperprefixHijack, self).__init__(attacker, victim, anns)
