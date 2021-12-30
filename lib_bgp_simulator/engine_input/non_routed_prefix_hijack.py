from .engine_input import EngineInput
from ..announcements import gen_attacker_prefix_ann


class NonRoutedPrefixHijack(EngineInput):
    __slots__ = ()

    def _get_announcements(self, **extra_ann_kwargs):
        extra_kwargs = {"roa_valid_length": True,
                        "roa_origin": 0}
        extra_kwargs.update(extra_ann_kwargs)
        return [gen_attacker_prefix_ann(self.AnnCls,
                                        self.attacker_asn,
                                        self.victim_asn,
                                        **extra_kwargs)]
