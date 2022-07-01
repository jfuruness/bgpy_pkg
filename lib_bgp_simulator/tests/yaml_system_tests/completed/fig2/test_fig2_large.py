from pathlib import Path

from ...graphs import Graph021
from ...utils import BaseGraphSystemTester

from ....engine_input import SubprefixHijack
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


class BaseFig2Tester(BaseGraphSystemTester):
    GraphInfoCls = Graph021
    EngineInputCls = SubprefixHijack
    base_dir = Path(__file__).parent
    adopting_asns = [18106, 6939, 207701, 42394, 22652]


class TestLargeFig2BGPSimple(BaseFig2Tester):
    BaseASCls = BGPSimpleAS
    AdoptASCls = BGPSimpleAS


class TestLargeFig2BGP(BaseFig2Tester):
    BaseASCls = BGPAS
    AdoptASCls = BGPAS


class TestLargeFig2ROVSimple(BaseFig2Tester):
    BaseASCls = BGPSimpleAS
    AdoptASCls = ROVSimpleAS


class TestLargeROV(BaseFig2Tester):
    BaseASCls = BGPAS
    AdoptASCls = ROVAS
