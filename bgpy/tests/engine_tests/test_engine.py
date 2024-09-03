from pathlib import Path

import pytest

from .engine_test_configs import engine_test_configs
from .utils import EngineTestConfig, EngineTester


@pytest.mark.engine
class TestEngine:
    """Performs a system test on the engine

    See README for in depth details
    """

    @pytest.mark.parametrize("conf", engine_test_configs)
    def test_engine(self, conf: EngineTestConfig, overwrite: bool, dpi: int | None):
        """Performs a system test on the engine

        See README for in depth details
        """

        EngineTester(
            base_dir=self.base_dir, conf=conf, overwrite=overwrite, dpi=dpi
        ).test_engine()

    @property
    def base_dir(self) -> Path:
        """Returns test output dir"""

        return Path(__file__).parent / "engine_test_outputs"
