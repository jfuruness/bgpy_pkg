from typing import Iterable

from bgpy.enums import ASGroups, Plane, PyOutcomes
from bgpy.simulation_frameworks.py_simulation_framework.metric_tracker.metric_key import (
    MetricKey,
)


def get_all_metric_keys() -> Iterable[MetricKey]:
    """Returns all possible metric key combos"""

    for plane in Plane:
        for as_group in ASGroups:
            for outcome in [x for x in PyOutcomes if x != PyOutcomes.UNDETERMINED]:
                yield MetricKey(plane=plane, as_group=as_group, outcome=outcome)
