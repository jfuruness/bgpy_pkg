from .attack import Attack
from ...announcements import gen_victim_prefix_ann
from ...announcements import gen_attacker_prefix_ann
from ...announcements import gen_attacker_superprefix_ann
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class SuperprefixPrefixHijack(Attack):
    __slots__ = tuple()

    def __init__(self,
                 attacker=ASNs.ATTACKER.value,
                 victim=ASNs.VICTIM.value,
                 **ann_kwargs):
        anns = [gen_victim_prefix_ann(AnnCls, victim, **ann_kwargs),
                gen_attacker_prefix_ann(AnnCls, attacker, **ann_kwargs),
                gen_attacker_superprefix_ann(AnnCls, attacker, **ann_kwargs)]
        super(SuperprefixPrefixHijack, self).__init__(attacker, victim, anns)
