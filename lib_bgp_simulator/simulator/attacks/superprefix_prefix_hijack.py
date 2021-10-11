from .attack import Attack
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships
from ...announcement import Announcement as Ann


class SuperprefixPrefixHijack(Attack):
    __slots__ = []
    def __init__(self, attacker=ASNs.ATTACKER.value, victim=ASNs.VICTIM.value, **extra_ann_kwargs):
        anns = [self.AnnCls(prefix=Prefixes.PREFIX.value,
                            timestamp=Timestamps.VICTIM.value,
                            as_path=(victim,),
                            seed_asn=victim,
                            roa_validity=ROAValidity.VALID,
                            recv_relationship=Relationships.ORIGIN,
                            withdraw=False,
                            traceback_end=False,
                            **extra_ann_kwargs),
                self.AnnCls(prefix=Prefixes.PREFIX.value,
                            timestamp=Timestamps.ATTACKER.value,
                            as_path=(attacker,),
                            seed_asn=attacker,
                            roa_validity=ROAValidity.INVALID,
                            recv_relationship=Relationships.ORIGIN,
                            withdraw=False,
                            traceback_end=False,
                            **extra_ann_kwargs),
                self.AnnCls(prefix=Prefixes.SUPERPREFIX.value,
                            timestamp=Timestamps.ATTACKER.value,
                            as_path=(attacker,),
                            seed_asn=attacker,
                            roa_validity=ROAValidity.UNKNOWN,
                            recv_relationship=Relationships.ORIGIN,
                            withdraw=False,
                            traceback_end=False,
                            **extra_ann_kwargs)]
        super(SuperprefixPrefixHijack, self).__init__(attacker, victim, anns)
