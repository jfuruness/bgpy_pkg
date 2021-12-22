from pathlib import Path

from ...graphs import Graph017
from ...utils import BaseGraphSystemTester

from ....engine_input import ValidPrefix
from ....announcements import gen_victim_prefix_ann
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


class InvalidReject(ValidPrefix):
    """Add a few extra ASNs to the path so they are rejected."""
    __slots__ = ()

    def _get_announcements(self, **extra_ann_kwargs):
        ann_kwargs = {"as_path": (self.victim_asn, 1, 2)}
        ann_kwargs.update(extra_ann_kwargs)
        return [gen_victim_prefix_ann(self.AnnCls,
                                      self.victim_asn,
                                      **ann_kwargs)]


class BaseBGPInvalidRejectTester(BaseGraphSystemTester):
    GraphInfoCls = Graph017
    EngineInputCls = InvalidReject
    base_dir = Path(__file__).parent


class Test001BGPInvalidReject(BaseBGPInvalidRejectTester):
    BaseASCls = BGPSimpleAS


class Test002BGPInvalidReject(BaseBGPInvalidRejectTester):
    BaseASCls = BGPAS


class Test003BGPInvalidReject(BaseBGPInvalidRejectTester):
    BaseASCls = ROVSimpleAS


class Test004BGPInvalidReject(BaseBGPInvalidRejectTester):
    BaseASCls = ROVAS
