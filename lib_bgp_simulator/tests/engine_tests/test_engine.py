import pytest

from .utils import EngineTester
from .utils import EngineTestConfig


class TestEngine:
    """Performs a system test on the engine

    See README for in depth details
    """

    @pytest.mark.parametrize("config",
                             [Cls() for Cls in EngineTestConfig.subclasses])
    def test_engine(config: EngineTestConfig):
        """Performs a system test on the engine

        See README for in depth details
        """

        EngineTester(base_dir=self.base_dir, test_conf=config).test_engine()

    @property
    def base_dir(self) -> Path:
        """Returns test output dir"""

        return Path(__file__).parent / "engine_test_outputs"
