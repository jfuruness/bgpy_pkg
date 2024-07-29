from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LineData:
    """Contains data for a specific line"""

    label: str
    formatted_graph_rows: Any
    line_info: LineInfo
    xs: tuple[float, ...]
    ys: tuple[float, ...]
    yerrs: tuple[float, ...]
