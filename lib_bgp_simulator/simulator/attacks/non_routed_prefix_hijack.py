from .attack import Attack
from ...announcements import gen_attacker_prefix_ann
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class NonRoutedPrefixHijack(Attack):
    __slots__ = ("victim_prefix", "attacker_prefix")

    def __init__(self,
                 attacker=ASNs.ATTACKER.value,
                 victim=None,
                 **extra_ann_kwargs):
        self.victim_prefix = None
        self.attacker_prefix = Prefixes.PREFIX.value

        anns = [gen_attacker_prefix_ann(self.AnnCls,
                                        attacker,
                                        **extra_ann_kwargs)]
        super(NonRoutedPrefixHijack, self).__init__(attacker, None, anns)
