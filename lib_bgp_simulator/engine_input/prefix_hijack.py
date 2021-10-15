from .engine_input import EngineInput
from ...announcements import gen_victim_prefix_ann, gen_attacker_prefix_ann
from ...enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class PrefixHijack(EngineInput):

    __slots__ = ()

    def _get_announcements(self, **extra_ann_kwargs):
        return [gen_victim_prefix_ann(self.AnnCls,
                                      self.victim_asn,
                                      **extra_ann_kwargs),
                gen_attacker_prefix_ann(self.AnnCls,
                                        attacker,
                                        **extra_ann_kwargs)]
