from pathlib import Path

from ...graphs import Graph001
from ...utils import BaseGraphSystemTester

from ....engine_input import SubprefixHijack
from ....engine import BGPSimpleAS
from ....engine import BGPAS


class BaseHiddenHijackTester(BaseGraphSystemTester):
    GraphInfoCls = Graph001
    EngineInputCls = SubprefixHijack
    base_dir = Path(__file__).parent


class Test001BGPSimpleHiddenHijack(BaseHiddenHijackTester):
    BaseASCls = BGPSimpleAS


class Test002BGPHiddenHijack(BaseHiddenHijackTester):
    BaseASCls = BGPAS
