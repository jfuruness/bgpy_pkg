from pathlib import Path
import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ...graphs import Graph002
from ...utils import BaseGraphSystemTester, YamlSystemTestRunner

from ....enums import ASNs
from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS



class BaseBGPPropTester(BaseGraphSystemTester):
    GraphInfoCls = Graph002
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
