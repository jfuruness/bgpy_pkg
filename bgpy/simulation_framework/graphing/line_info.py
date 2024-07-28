from dataclasses import dataclass


@dataclass(frozen=True)
class LineInfo:
    """Contains info for how a line should be plotted on a graph"""

    label: str
    marker: str
    ls: str
    unrelated_to_adoption: bool = False
    hardcoded_xs: tuple[float, ...] = ()
    hardcoded_ys: tuple[float, ...] = ()
    hardcoded_yerrs: tuple[float, ...] = ()
