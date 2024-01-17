from typing import Iterable

from bgpy.enums import ASGroups, Plane, PyOutcomes
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey


def get_all_metric_keys() -> Iterable[MetricKey]:
    """Returns all possible metric key combos"""

    for plane in [Plane.DATA]:
        for as_group in [ASGroups.ALL_WOUT_IXPS]:
            for outcome in [x for x in PyOutcomes if x != PyOutcomes.UNDETERMINED]:
                yield MetricKey(plane=plane, as_group=as_group, outcome=outcome)
