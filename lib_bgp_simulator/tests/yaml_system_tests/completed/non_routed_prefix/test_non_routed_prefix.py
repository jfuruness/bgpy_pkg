from pathlib import Path

from lib_bgp_simulator.tests.graphs import Graph006
from lib_bgp_simulator.tests.utils import BaseGraphSystemTester

from lib_bgp_simulator.engine_input import NonRoutedPrefixHijack
from lib_bgp_simulator.engine import BGPSimpleAS
from lib_bgp_simulator.engine import BGPAS
from lib_bgp_simulator.engine import ROVSimpleAS
from lib_bgp_simulator.engine import ROVAS


class BaseNonRoutedPrefixTester(BaseGraphSystemTester):
    GraphInfoCls = Graph006
    EngineInputCls = NonRoutedPrefixHijack
    base_dir = Path(__file__).parent
    adopting_asns = (2,)


class Test013NonRoutedPrefixROVSimple(BaseNonRoutedPrefixTester):
    BaseASCls = BGPSimpleAS
    AdoptASCls = ROVSimpleAS


class Test014NonRoutedPrefix2ROV(BaseNonRoutedPrefixTester):
    BaseASCls = BGPAS
    AdoptASCls = ROVAS
