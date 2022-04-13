from .engine_input import EngineInput
from ..announcements import gen_attacker_prefix_ann
from ..announcements import gen_attacker_superprefix_ann


class NonRoutedSuperprefixPrefixHijack(EngineInput):
    __slots__ = tuple()

    def _get_announcements(self, **ann_kwargs):
        return [gen_attacker_prefix_ann(self.AnnCls,
                                        self.attacker_asn,
                                        self.victim_asn,
                                        **ann_kwargs),
                gen_attacker_superprefix_ann(self.AnnCls,
                                             self.attacker_asn,
                                             **ann_kwargs)]
