from .engine_input import EngineInput
from ..announcements import gen_victim_prefix_ann
from ..announcements import gen_attacker_subprefix_ann
from ..enums import Prefixes


class SubprefixHijack(EngineInput):
    __slots__ = ("victim_prefix", "attacker_prefix")

    def __init__(self, *args, **kwargs):

        self.victim_prefix = Prefixes.PREFIX.value
        self.attacker_prefix = Prefixes.SUBPREFIX.value
        super(SubprefixHijack, self).__init__(*args, **kwargs)

    def _get_announcements(self, **extra_ann_kwargs):
        return [gen_victim_prefix_ann(self.AnnCls,
                                      self.victim_asn,
                                      **extra_ann_kwargs),
                gen_attacker_subprefix_ann(self.AnnCls,
                                           self.attacker_asn,
                                           **extra_ann_kwargs)]
