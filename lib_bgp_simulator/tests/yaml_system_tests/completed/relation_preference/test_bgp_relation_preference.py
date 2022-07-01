from pathlib import Path

from lib_bgp_simulator.tests.graphs import Graph017
from lib_bgp_simulator.tests.utils import BaseGraphSystemTester

from lib_bgp_simulator.engine_input import ValidPrefix
from lib_bgp_simulator.engine import BGPSimpleAS
from lib_bgp_simulator.engine import BGPAS
from lib_bgp_simulator.engine import ROVSimpleAS
from lib_bgp_simulator.engine import ROVAS


class BaseBGPRelationPreferenceTester(BaseGraphSystemTester):
    GraphInfoCls = Graph017
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent


class Test019BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = BGPSimpleAS


class Test020BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = BGPAS


class Test021BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = ROVSimpleAS


class Test022BGPRelationPreference(BaseBGPRelationPreferenceTester):
    BaseASCls = ROVAS
