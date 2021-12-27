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
    """Test seeded routes can never be withdrawn.

    Regardless of the graph used, this engine_input will always attempt to leak
    from AS 666.
    """
    __slots__ = ()

    def post_propagation_hook(self, engine: SimulatorEngine,
                              prev_data_point: DataPoint, *args, **kwargs):
        # Route leak from AS 666 to cause withdrawals to be sent
        attacker_ann = None
        attacker_ann = engine.as_dict[666]._local_rib.get_ann(Prefixes.PREFIX.value) # noqa E501
        if prev_data_point.propagation_round == 0:
            # Set AS 4's ann to seeded so it isn't overridden
            engine.as_dict[4]._local_rib.get_ann(Prefixes.PREFIX.value).seed_asn = 4 # noqa E501
            # Leak AS 666's ann
            engine.as_dict[666]._local_rib.get_ann(Prefixes.PREFIX.value).recv_relationship = Relationships.CUSTOMERS # noqa E501


class BaseBGPWithdrawSeededTester(BaseGraphSystemTester):
    GraphInfoCls = Graph020
    EngineInputCls = RouteLeakAS1
    propagation_rounds = 2
    base_dir = Path(__file__).parent


class Test001BGPWithdrawSeeded(BaseBGPWithdrawSeededTester):
    """Test basic withdrawal functionality in simple bgp class.

    Despite the lack of withdrawal support in the simple classes, this test
    will still pass. That is because the announcement is being overridden by a
    better one. Overriding announcements is allowed in the simple classes, but
    not in the full BGP class (because announcements should be withdrawn and
    then replaced, rather than overridden).
    """
    BaseASCls = BGPSimpleAS


class Test002BGPWithdrawSeeded(BaseBGPWithdrawSeededTester):
    BaseASCls = BGPAS


class Test003BGPWithdrawSeeded(BaseBGPWithdrawSeededTester):
    BaseASCls = ROVSimpleAS


class Test004BGPWithdrawSeeded(BaseBGPWithdrawSeededTester):
    BaseASCls = ROVAS
