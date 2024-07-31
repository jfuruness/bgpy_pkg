from dataclasses import dataclass

from .line_properties_generator import LinePropertiesGenerator

GENERATOR = LinePropertiesGenerator()


@dataclass(frozen=True)
class LineInfo:
    """Contains info for how a line should be plotted on a graph"""

    label: str
    marker: str = ""
    ls: str = ""
    color: str = ""
    unrelated_to_adoption: bool = False
    hardcoded_xs: tuple[float, ...] = ()
    hardcoded_ys: tuple[float, ...] = ()
    hardcoded_yerrs: tuple[float, ...] = ()
    # Set to none for aggregating strongest attackerinternally
    _fmt: str = ""

    def __post_init__(self):
        assert len(self.hardcoded_xs) == len(self.hardcoded_ys)
        assert len(self.hardcoded_ys) == len(self.hardcoded_yerrs)
        if not self.marker:
            object.__setattr__(self, "marker", GENERATOR.get_marker())
        if not self.ls:
            object.__setattr__(self, "ls", GENERATOR.get_line_style())
        if not self.color:
            object.__setattr__(self, "color", GENERATOR.get_color())
