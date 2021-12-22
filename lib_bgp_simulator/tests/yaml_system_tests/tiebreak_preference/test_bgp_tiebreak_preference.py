from pathlib import Path

from ...graphs import Graph019
from ...utils import BaseGraphSystemTester

from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS

class BaseBGPTiebreakPreferenceTester(BaseGraphSystemTester):
    GraphInfoCls = Graph019
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent

class Test001BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = BGPSimpleAS

class Test002BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = BGPAS

class Test003BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = ROVSimpleAS

class Test004BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = ROVAS


