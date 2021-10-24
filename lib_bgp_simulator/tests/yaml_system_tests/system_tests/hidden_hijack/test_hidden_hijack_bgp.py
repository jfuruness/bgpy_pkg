from pathlib import Path
import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ...graphs import HiddenHijackGraphInfo
from ...utils import BaseGraphSystemTester, YamlSystemTestRunner

from .....enums import ASNs
from .....engine_input import SubprefixHijack
from .....engine import BGPAS
from .....engine import BGPRIBsAS


class BaseHiddenHijackTester(BaseGraphSystemTester):
    GraphInfoCls = HiddenHijackGraphInfo
    EngineInputCls = SubprefixHijack
    base_dir = Path(__file__).parent

    @property
    def as_classes(self):
        return {asn: self.BaseASCls for asn in
                list(range(1, 4)) + [ASNs.VICTIM.value, ASNs.ATTACKER.value]}

class TestBGPSimpleHiddenHijack(BaseHiddenHijackTester):
    BaseASCls = BGPAS

class TestBGPHiddenHijack(BaseHiddenHijackTester):
    BaseASCls = BGPRIBsAS
