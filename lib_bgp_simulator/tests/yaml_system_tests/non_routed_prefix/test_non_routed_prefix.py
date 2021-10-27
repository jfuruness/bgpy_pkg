from pathlib import Path

from ...graphs import Graph006
from ...utils import BaseGraphSystemTester

from ....engine_input import NonRoutedPrefixHijack
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


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
