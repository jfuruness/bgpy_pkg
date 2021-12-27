from pathlib import Path

from ...graphs import Graph021
from ...utils import BaseGraphSystemTester

from ....enums import Prefixes, Relationships
from ....engine_input import ValidPrefix
from ....engine import BGPSimpleAS
from ....engine import BGPAS
from ....engine import ROVSimpleAS
from ....engine import ROVAS
from ....engine import SimulatorEngine
from ....simulator import DataPoint


class RouteLeakAS1Poisoned(ValidPrefix):
    """Test propagation for withdrawals using a path-poisoned route leak.

    Regardless of the graph used, this engine_input will always attempt to leak
    from AS 666.
    """
    __slots__ = ()

    def post_propagation_hook(self, engine: SimulatorEngine,
                              prev_data_point: DataPoint, *args, **kwargs):
        # Route leak from AS 1 to cause withdrawals to be sent
        attacker_ann = None
        attacker_ann = engine.as_dict[666]._local_rib.get_ann(Prefixes.PREFIX.value) # noqa E501
        if prev_data_point.propagation_round == 0:
            engine.as_dict[666]._local_rib.get_ann(Prefixes.PREFIX.value).recv_relationship = Relationships.CUSTOMERS # noqa E501
            as_path = engine.as_dict[666]._local_rib.get_ann(Prefixes.PREFIX.value).as_path # noqa E501
            engine.as_dict[666]._local_rib.get_ann(Prefixes.PREFIX.value).as_path = (666, 777, 4)  # noqa E501


class BaseBGPWithdrawPropTester(BaseGraphSystemTester):
    GraphInfoCls = Graph021
    EngineInputCls = RouteLeakAS1Poisoned
    propagation_rounds = 2
    base_dir = Path(__file__).parent


class Test001BGPWithdrawProp(BaseBGPWithdrawPropTester):
    """Test withdrawal propagation in BGP Simple AS.

    This test is an expected fail. The test is here to provide an example of a
    scenario when the experiment requires use of the BGPAS class instead of the
    BGPSimpleAS. The BGPSimpleASes 4 and 5 in the round 1 generated graph still
    have routes to the prefix, however, this is incorrect. Correct behavior is
    shown by the BGPASes, which do not have routes after the path-poisoned
    route leak by AS 1.

    """
    BaseASCls = BGPSimpleAS


class Test002BGPWithdrawProp(BaseBGPWithdrawPropTester):
    BaseASCls = BGPAS


class Test003BGPWithdrawProp(BaseBGPWithdrawPropTester):
    BaseASCls = ROVSimpleAS


class Test004BGPWithdrawProp(BaseBGPWithdrawPropTester):
    BaseASCls = ROVAS
