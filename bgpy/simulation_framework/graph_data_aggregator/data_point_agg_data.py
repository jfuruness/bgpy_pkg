from dataclasses import dataclass

from .data_point_key import DataPointKey


@dataclass(frozen=True, slots=True)
class DataPointAggData:
    """Data for a single point in a single graph that's an aggregate of trials"""

    value: float
    yerr: float
    data_point_key: DataPointKey
