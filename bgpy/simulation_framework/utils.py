from typing import Any, Iterable, Optional

from frozendict import frozendict

from bgpy.caida_collector import CaidaCollector

from bgpy.enums import ASGroups, Plane, Outcomes
from bgpy.simulation_engine import BGPSimpleAS
from bgpy.simulation_engine import RealROVSimpleAS
from bgpy.simulation_engine import RealPeerROVSimpleAS
from bgpy.simulation_engine import SimulationEngine
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey


def get_real_world_rov_asn_cls_dict(
    min_rov_confidence: float = 0, caida_run_kwargs: Optional[dict[Any, Any]] = None
) -> frozendict[int, type[BGPSimpleAS]]:
    """Gets real world ROV ASes, and creates a dict of asn: AS Class

    There are unique probabilities for each ROV AS, and additionally
    some ROV ASes are peer filtering only

    min_rov_confidence of 0 will take all ASes
    """

    asn_as_cls_dict = dict()

    if caida_run_kwargs is None:
        caida_run_kwargs = {"tsv_path": None}

    engine = CaidaCollector(BaseASCls=BGPSimpleAS, GraphCls=SimulationEngine).run(
        **caida_run_kwargs
    )

    for as_ in engine:
        if as_.rov_confidence >= min_rov_confidence:
            if as_.rov_filtering == "all":
                asn_as_cls_dict[as_.asn] = RealROVSimpleAS
            elif as_.rov_filtering == "peers":
                asn_as_cls_dict[as_.asn] = RealPeerROVSimpleAS
            else:
                raise NotImplementedError(
                    f"ROV filtering case not accounted for: {as_.rov_filtering}"
                )

    return frozendict({int(k): v for k, v in asn_as_cls_dict.items()})


def get_all_metric_keys() -> Iterable[MetricKey]:
    """Returns all possible metric key combos"""

    for plane in Plane:
        for as_group in ASGroups:
            for outcome in [x for x in Outcomes if x != Outcomes.UNDETERMINED]:
                yield MetricKey(plane=plane, as_group=as_group, outcome=outcome)
