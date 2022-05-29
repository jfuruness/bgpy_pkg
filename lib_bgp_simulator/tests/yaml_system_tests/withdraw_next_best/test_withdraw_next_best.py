from pathlib import Path

from ...graphs import Graph042
from ...utils import BaseGraphSystemTester

from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS

from ..withdraw_prop import RouteLeakAS1Poisoned


class BaseBGPWithdrawNextBestTester(BaseGraphSystemTester):
    GraphInfoCls = Graph042
    EngineInputCls = RouteLeakAS1Poisoned
    propagation_rounds = 2
    base_dir = Path(__file__).parent


class Test001BGPWithdrawNextBest(BaseBGPWithdrawNextBestTester):
    """Test selection of next-best announcement after withdraw in BGPSimpleAS.

    This test is expected to produce an incorrect graph. The test is here to
    provide an example of a scenario when the experiment requires use of the
    BGPAS class instead of the BGPSimpleAS. The BGPSimpleASes 4 and 5 in the
    round 1 generated graph still have old, no-longer-announced route from AS 4
    to the prefix, however, this is incorrect. Correct behavior is shown by the
    BGPASes, which have selected the route from AS 3 after the path-poisoned
    route leak by AS 666.

    """
    BaseASCls = BGPSimpleAS


class Test002BGPWithdrawNextBest(BaseBGPWithdrawNextBestTester):
    BaseASCls = BGPAS


class Test003BGPWithdrawNextBest(BaseBGPWithdrawNextBestTester):
    BaseASCls = ROVSimpleAS


class Test004BGPWithdrawNextBest(BaseBGPWithdrawNextBestTester):
    BaseASCls = ROVAS
