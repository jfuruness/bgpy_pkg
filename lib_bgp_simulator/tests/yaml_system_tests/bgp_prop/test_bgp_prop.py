from pathlib import Path

from ...graphs import Graph002
from ...utils import BaseGraphSystemTester

from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


class BaseBGPPropTester(BaseGraphSystemTester):
    GraphInfoCls = Graph002
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent


class Test003BGPSimpleProp(BaseBGPPropTester):
    BaseASCls = BGPSimpleAS


class Test004BGPProp(BaseBGPPropTester):
    BaseASCls = BGPAS


class Test005BGPSimpleProp(BaseBGPPropTester):
    BaseASCls = ROVSimpleAS


class Test006BGPProp(BaseBGPPropTester):
    BaseASCls = ROVAS
