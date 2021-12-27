from pathlib import Path

from ...graphs import Graph020
from ...utils import BaseGraphSystemTester

from ....enums import Prefixes, Relationships
from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS
from ....engine import SimulatorEngine
from ....simulator import DataPoint


class RouteLeakAS1(ValidPrefix):
    """Test common case for withdrawals using a route leak.

    Regardless of the graph used, this engine_input will always attempt to leak
    from AS 1.
    """
    __slots__ = ()

    def post_propagation_hook(self, engine: SimulatorEngine,
                              prev_data_point: DataPoint, *args, **kwargs):
        # Route leak from AS 1 to cause withdrawals to be sent
        attacker_ann = None
        attacker_ann = engine.as_dict[1]._local_rib.get_ann(Prefixes.PREFIX.value) # noqa E501
        if prev_data_point.propagation_round == 0:
            engine.as_dict[1]._local_rib.get_ann(Prefixes.PREFIX.value).recv_relationship = Relationships.CUSTOMERS # noqa E501


class BaseBGPWithdrawBasicTester(BaseGraphSystemTester):
    GraphInfoCls = Graph020
    EngineInputCls = RouteLeakAS1
    propagation_rounds = 2
    base_dir = Path(__file__).parent


class Test001BGPWithdrawBasic(BaseBGPWithdrawBasicTester):
    """Test basic withdrawal functionality in simple bgp class.

    Despite the lack of withdrawal support in the simple classes, this test
    will still pass. That is because the announcement is being overridden by a
    better one. Overriding announcements is allowed in the simple classes, but
    not in the full BGP class (because announcements should be withdrawn and
    then replaced, rather than overridden).
    """
    BaseASCls = BGPSimpleAS


class Test002BGPWithdrawBasic(BaseBGPWithdrawBasicTester):
    BaseASCls = BGPAS


class Test003BGPWithdrawBasic(BaseBGPWithdrawBasicTester):
    BaseASCls = ROVSimpleAS


class Test004BGPWithdrawBasic(BaseBGPWithdrawBasicTester):
    BaseASCls = ROVAS
