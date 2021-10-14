from .attack import Attack
from ...announcements import gen_victim_prefix_ann
from ...announcements import gen_attacker_subprefix_ann
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class SubprefixHijack(Attack):
    __slots__ = ("victim_prefix", "attacker_prefix")

    def __init__(self,
                 attacker=ASNs.ATTACKER.value,
                 victim=ASNs.VICTIM.value,
                 **ann_kwargs):

        self.victim_prefix = Prefixes.PREFIX.value
        self.attacker_prefix = Prefixes.SUBPREFIX.value

        anns = [gen_victim_prefix_ann(AnnCls, victim, **ann_kwargs),
                gen_attacker_subprefix_ann(AnnCls, attacker, **ann_kwargs)]
        super(SubprefixHijack, self).__init__(attacker, victim, anns)
