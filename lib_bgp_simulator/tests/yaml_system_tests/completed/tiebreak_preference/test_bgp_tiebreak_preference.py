from pathlib import Path

from lib_bgp_simulator.tests.graphs import Graph019
from lib_bgp_simulator.tests.utils import BaseGraphSystemTester

from lib_bgp_simulator.engine_input import ValidPrefix
from lib_bgp_simulator.engine import BGPSimpleAS
from lib_bgp_simulator.engine import BGPAS
from lib_bgp_simulator.engine import ROVSimpleAS
from lib_bgp_simulator.engine import ROVAS


class BaseBGPTiebreakPreferenceTester(BaseGraphSystemTester):
    GraphInfoCls = Graph019
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent


class Test023BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = BGPSimpleAS


class Test024BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = BGPAS


class Test025BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = ROVSimpleAS


class Test026BGPTiebreakPreference(BaseBGPTiebreakPreferenceTester):
    BaseASCls = ROVAS
