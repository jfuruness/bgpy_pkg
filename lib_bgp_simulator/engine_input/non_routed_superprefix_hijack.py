from .engine_input import EngineInput
from ..announcements import gen_attacker_superprefix_ann


class NonRoutedSuperprefixHijack(EngineInput):
    __slots__ = tuple()

    def _get_announcements(self, **extra_ann_kwargs):
        return [gen_attacker_superprefix_ann(self.AnnCls,
                                             self.attacker_asn,
                                             **extra_ann_kwargs)]
