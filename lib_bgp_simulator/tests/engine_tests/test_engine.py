from pathlib import Path

import pytest

from .engine_test_configs import Config001
from .utils import EngineTester
from .utils import EngineTestConfig


class TestEngine:
    """Performs a system test on the engine

    See README for in depth details
    """

    @pytest.mark.parametrize("conf",
    #                         [Cls() for Cls in EngineTestConfig.subclasses])
                             [Config001])
    def test_engine(self, conf: EngineTestConfig):
        """Performs a system test on the engine

        See README for in depth details
        """

        EngineTester(base_dir=self.base_dir, conf=conf).test_engine()

    @property
    def base_dir(self) -> Path:
        """Returns test output dir"""

        return Path(__file__).parent / "engine_test_outputs"
