from pathlib import Path

from ...graphs import Graph017
from ...utils import BaseGraphSystemTester

from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


class BaseBGPRelationPreferenceTester(BaseGraphSystemTester):
    GraphInfoCls = Graph017
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent


class Test001BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = BGPSimpleAS


class Test002BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = BGPAS


class Test003BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = ROVSimpleAS


class Test004BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = ROVAS
