from pathlib import Path

from ...graphs import Graph016
from ...utils import BaseGraphSystemTester

from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS


class Test027BadDiagram(BaseGraphSystemTester):
    GraphInfoCls = Graph016
    EngineInputCls = ValidPrefix
    base_dir = Path(__file__).parent
    BaseASCls = BGPSimpleAS
