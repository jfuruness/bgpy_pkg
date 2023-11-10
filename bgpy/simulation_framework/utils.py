from typing import Any, Iterable, Optional

from frozendict import frozendict

from bgpy.caida_collector import CaidaCollector

from bgpy.enums import ASGroups, Plane, Outcomes
from bgpy.simulation_engine import BGPSimplePolicy
from bgpy.simulation_engine import RealROVSimplePolicy
from bgpy.simulation_engine import RealPeerROVSimplePolicy
from bgpy.simulation_engine import SimulationEngine
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey


def get_real_world_rov_asn_cls_dict(
    min_rov_confidence: float = 0,
    caida_run_kwargs: Optional[dict[Any, Any]] = None,
    CaidaCollectorCls=CaidaCollector,
) -> frozendict[int, type[BGPSimplePolicy]]:
    """Gets real world ROV Policyes, and creates a dict of asn: Policy Class

    There are unique probabilities for each ROV Policy, and additionally
    some ROV Policyes are peer filtering only

    min_rov_confidence of 0 will take all Policyes
    """

    asn_as_cls_dict = dict()

    if caida_run_kwargs is None:
        caida_run_kwargs = {"tsv_path": None}

    engine = CaidaCollectorCls(
        BasePolicyCls=BGPSimplePolicy, GraphCls=SimulationEngine
    ).run(**caida_run_kwargs)

    for as_ in engine:
        if as_.rov_confidence >= min_rov_confidence:
            if as_.rov_filtering == "all":
                asn_as_cls_dict[as_.asn] = RealROVSimplePolicy
            elif as_.rov_filtering == "peers":
                asn_as_cls_dict[as_.asn] = RealPeerROVSimplePolicy
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
