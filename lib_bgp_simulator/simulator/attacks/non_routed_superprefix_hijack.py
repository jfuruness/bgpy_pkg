from .attack import Attack
from ...announcements import gen_superprefix_ann
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class NonRoutedSuperprefixHijack(Attack):
    __slots__ = tuple()

    def __init__(self,
                 attacker=ASNs.ATTACKER.value,
                 victim=ASNs.VICTIM.value,
                 **extra_ann_kwargs):
        anns = [gen_superprefix_ann(self.AnnCls, attacker, **extra_ann_kwargs)]
        super(NonRoutedSuperprefixHijack, self).__init__(attacker,
                                                         victim,
                                                         anns)
