from .engine_input import EngineInput
from ..announcements import gen_attacker_prefix_ann


class NonRoutedPrefixHijack(EngineInput):
    __slots__ = ()

    def _get_announcements(self, **extra_ann_kwargs):
        return [gen_attacker_prefix_ann(self.AnnCls,
                                        self.attacker_asn,
                                        **extra_ann_kwargs)]
