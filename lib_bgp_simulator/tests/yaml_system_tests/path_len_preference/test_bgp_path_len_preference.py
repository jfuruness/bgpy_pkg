from pathlib import Path

from ...graphs import Graph018
from ...utils import BaseGraphSystemTester

from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS

class BaseBGPPathLenPreferenceTester(BaseGraphSystemTester):
    GraphInfoCls = Graph018
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent

class Test001BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = BGPSimpleAS

class Test002BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = BGPAS

class Test003BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = ROVSimpleAS

class Test004BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = ROVAS


