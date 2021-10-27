from pathlib import Path

from ...graphs import Graph006
from ...utils import BaseGraphSystemTester

from ....engine_input import NonRoutedSuperprefixHijack
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


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
