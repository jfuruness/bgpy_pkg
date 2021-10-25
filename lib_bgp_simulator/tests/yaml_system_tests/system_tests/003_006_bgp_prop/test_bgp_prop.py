from pathlib import Path
import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ...graphs import G001HiddenHijackGraphInfo
from ...utils import BaseGraphSystemTester, YamlSystemTestRunner

from .....enums import ASNs
from .....engine_input import SubprefixHijack
from .....engine import BGPSimpleAS
from .....engine import BGPAS


class BaseBGPPropTester(BaseGraphSystemTester):
    GraphInfoCls = G002
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent

    @property
    def as_classes(self):
        return {asn: self.BaseASCls for asn in
                list(range(1, 8)) + [ASNs.VICTIM.value, ASNs.ATTACKER.value]}

class Test003BGPSimpleProp(BaseBGPPropTester):
    BaseASCls = BGPSimpleAS

class Test004BGPProp(BaseBGPPropTester):
    BaseASCls = BGPAS

class Test005BGPSimpleProp(BaseBGPPropTester):
    BaseASCls = ROVSimpleAS

class Test006BGPProp(BaseBGPPropTester):
    BaseASCls = ROVAS
