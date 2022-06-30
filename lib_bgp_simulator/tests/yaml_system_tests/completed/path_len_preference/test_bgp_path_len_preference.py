from pathlib import Path

from lib_bgp_simulator.tests.graphs import Graph018
from lib_bgp_simulator.tests.utils import BaseGraphSystemTester

from lib_bgp_simulator.engine_input import ValidPrefix
from lib_bgp_simulator.engine import BGPSimpleAS
from lib_bgp_simulator.engine import BGPAS
from lib_bgp_simulator.engine import ROVSimpleAS
from lib_bgp_simulator.engine import ROVAS


class BaseBGPPathLenPreferenceTester(BaseGraphSystemTester):
    GraphInfoCls = Graph018
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent


class Test015BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = BGPSimpleAS


class Test016BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = BGPAS


class Test017BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = ROVSimpleAS


class Test018BGPPathLenPreference(BaseBGPPathLenPreferenceTester):
    BaseASCls = ROVAS
