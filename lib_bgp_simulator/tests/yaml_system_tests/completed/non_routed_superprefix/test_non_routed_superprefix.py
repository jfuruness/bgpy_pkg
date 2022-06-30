from pathlib import Path

from lib_bgp_simulator.tests.graphs import Graph006
from lib_bgp_simulator.tests.utils import BaseGraphSystemTester

from lib_bgp_simulator.engine_input import NonRoutedSuperprefixHijack
from lib_bgp_simulator.engine import BGPSimpleAS
from lib_bgp_simulator.engine import BGPAS
from lib_bgp_simulator.engine import ROVSimpleAS
from lib_bgp_simulator.engine import ROVAS


class BaseNonRoutedSuperprefixTester(BaseGraphSystemTester):
    GraphInfoCls = Graph006
    EngineInputCls = NonRoutedSuperprefixHijack
    base_dir = Path(__file__).parent
    adopting_asns = [2]


class Test011NonRoutedSuperprefixROVSimple(BaseNonRoutedSuperprefixTester):
    BaseASCls = BGPSimpleAS
    AdoptASCls = ROVSimpleAS


class Test012NonRoutedSuperprefix2ROV(BaseNonRoutedSuperprefixTester):
    BaseASCls = BGPAS
    AdoptASCls = ROVAS
