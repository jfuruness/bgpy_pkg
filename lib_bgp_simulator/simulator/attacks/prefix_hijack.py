from .attack import Attack
from ...announcements import gen_victim_prefix_ann, gen_attacker_prefix_ann
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class PrefixHijack(Attack):

    __slots__ = ("victim_prefix", "attacker_prefix")

    def __init__(self,
                 attacker=ASNs.ATTACKER.value,
                 victim=ASNs.VICTIM.value,
                 **extra_ann_kwargs):
        self.victim_prefix = Prefixes.PREFIX.value
        self.attacker_prefix = Prefixes.PREFIX.value
        anns = [gen_victim_prefix_ann(AnnCls, victim, **extra_ann_kwargs),
                gen_attacker_prefix_ann(AnnCls, attacker, **extra_ann_kwargs)]
        super(PrefixHijack, self).__init__(attacker, victim, anns)
