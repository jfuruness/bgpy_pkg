from .engine_input import EngineInput
from ..announcements import gen_superprefix_ann
from ..enums import Prefixes, Timestamps, ASNs, ROAValidity, Relationships


class NonRoutedSuperprefixHijack(EngineInput):
    __slots__ = tuple()

    def _get_announcements(self, **extra_ann_kwargs):
        return [gen_superprefix_ann(self.AnnCls,
                                    self.attacker_asn,
                                    **extra_ann_kwargs)]
