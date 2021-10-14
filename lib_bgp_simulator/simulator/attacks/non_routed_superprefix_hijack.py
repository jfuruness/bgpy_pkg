from .attack import Attack
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class NonRoutedSuperprefixHijack(Attack):
    __slots__ = tuple()

    def __init__(self,
                 attacker=ASNs.ATTACKER.value,
                 victim=ASNs.VICTIM.value,
                 **extra_ann_kwargs):
        anns = [self.AnnCls(prefix=Prefixes.SUPERPREFIX.value,
                            timestamp=Timestamps.ATTACKER.value,
                            as_path=(attacker,),
                            seed_asn=attacker,
                            roa_validity=ROAValidity.UNKNOWN,
                            recv_relationship=Relationships.ORIGIN,
                            withdraw=False,
                            traceback_end=False,
                            **extra_ann_kwargs)]
        super(NonRoutedSuperprefixHijack, self).__init__(attacker,
                                                         victim,
                                                         anns)
