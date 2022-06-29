from pathlib import Path

import pytest

from .engine_test_configs import Config001
from .engine_test_configs import Config002
from .engine_test_configs import Config003
from .engine_test_configs import Config004
from .engine_test_configs import Config005
from .utils import EngineTester
from .utils import EngineTestConfig


class TestEngine:
    """Performs a system test on the engine

    See README for in depth details
    """

    @pytest.mark.parametrize("conf",
    #                         [Cls() for Cls in EngineTestConfig.subclasses])
                             [Config001, Config002, Config003, Config004, Config005])
    def test_engine(self, conf: EngineTestConfig, overwrite: bool):
        """Performs a system test on the engine

        See README for in depth details
        """

        EngineTester(base_dir=self.base_dir,
                     conf=conf,
                     overwrite=overwrite).test_engine()

    @property
    def base_dir(self) -> Path:
        """Returns test output dir"""

        return Path(__file__).parent / "engine_test_outputs"
