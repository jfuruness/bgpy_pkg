from typing import Dict
from typing import Type

from caida_collector_pkg import CaidaCollector

from ..simulation_engine import BGPSimpleAS
from ..simulation_engine import RealROVSimpleAS
from ..simulation_engine import RealPeerROVSimpleAS
from ..simulation_engine import SimulationEngine


def get_real_world_rov_asn_cls_dict(
    self,
    min_rov_confidence: float = 0,
) -> Dict[int, Type[BGPSimpleAS]]:
    """Gets real world ROV ASes, and creates a dict of asn: AS Class

    There are unique probabilities for each ROV AS, and additionally
    some ROV ASes are peer filtering only

    min_rov_confidence of 0 will take all ASes
    """

    asn_as_cls_dict = dict()

    engine = CaidaCollector(BaseASCls=BGPSimpleAS, GraphCls=SimulationEngine).run(
        tsv_path=None
    )

    for as_ in engine:
        if as_.rov_confidence >= min_rov_confidence:
            if as_.rov_filtering == "all":
                asn_as_cls_dict[as_.asn] = RealROVSimpleAS
            elif as_.rov_filtering == "peer":
                asn_as_cls_dict[as_.asn] = RealPeerROVSimpleAS
            else:
                raise NotImplementedError("ROV filtering case not accoutned for")

    return asn_as_cls_dict
