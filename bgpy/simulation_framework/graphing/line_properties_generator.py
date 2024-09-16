from itertools import cycle


class LinePropertiesGenerator:
    """Generators colors, markers, and line styles"""

    def __init__(self) -> None:
        self._markers_cycle: cycle[str] = cycle(self._expand(self.accepted_markers))
        self._line_styles_cycle: cycle[str] = cycle(
            self._expand(self.accepted_line_styles)
        )
        self._colors_cycle: cycle[str] = cycle(self._expand(self.accepted_colors))

    def get_marker(self) -> str:
        return next(self._markers_cycle)

    def get_line_style(self) -> str:
        return next(self._line_styles_cycle)

    def get_color(self) -> str:
        return next(self._colors_cycle)

    def _expand(self, options: list[str]) -> list[str]:
        """Expands options in a good pattern"""

        new_options = options.copy() + options.copy()[0:-2:2]
        new_options += new_options.copy()[::-1]
        return new_options

    @property
    def accepted_markers(self) -> list[str]:
        """Returns markers allowed for papers"""

        return [".", "1", "*", "x", "d", "2", "3", "4", "v", "+", "s"]

    @property
    def accepted_line_styles(self) -> list[str]:
        """Returns line_styles allowed for papers"""

        return [
            "-",
            "--",
            "-.",
            ":",
            "solid",
            "dotted",
            "dashdot",
            "dashed",
        ]

    @property
    def accepted_colors(self) -> list[str]:
        """Returns colors allowed for papers"""

        return [
            "b",
            "g",
            "r",
            "c",
            "m",
            "y",
            "darkorange",
            "darkgoldenrod",
            "lightcoral",
            "sienna",
            "gold",
            "darkolivegreen",
            "steelblue",
        ]
