from dataclasses import dataclass
from typing import ClassVar

from bgpy.utils import EngineRunConfig


@dataclass(frozen=True, slots=True)
class EngineTestConfig(EngineRunConfig):
    """Configuration info for the test suite"""

    _used_names: ClassVar[set[str]] = set()

    def __post_init__(self):
        """Names are used as folder names for testing, can't have duplicates"""

        if self.name in EngineTestConfig._used_names:
            raise ValueError(f"The name '{self.name}' is already in use.")
        EngineTestConfig._used_names.add(self.name)
