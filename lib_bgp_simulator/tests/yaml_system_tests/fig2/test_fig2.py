from pathlib import Path

import pytest

from ...graphs import Graph003
from ...utils import BaseGraphSystemTester

from ....enums import ASNs
from ....engine_input import SubprefixHijack
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS


class BaseFig2Tester(BaseGraphSystemTester):
    GraphInfoCls = Graph003
    EngineInputCls = SubprefixHijack
    base_dir = Path(__file__).parent
    adopting_asns = [3, 4]


class Test007Fig2BGPSimple(BaseFig2Tester):
    BaseASCls = BGPSimpleAS
    AdoptASCls = BGPSimpleAS


class Test008Fig2BGP(BaseFig2Tester):
    BaseASCls = BGPAS
    AdoptASCls = BGPAS


class Test009Fig2ROVSimple(BaseFig2Tester):
    BaseASCls = BGPSimpleAS
    AdoptASCls = ROVSimpleAS


class Test010ROV(BaseFig2Tester):
    BaseASCls = BGPAS
    AdoptASCls = ROVAS
