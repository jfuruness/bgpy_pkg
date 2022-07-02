from pathlib import Path

import pytest

from .engine_test_configs import Config001
from .engine_test_configs import Config002
from .engine_test_configs import Config003
from .engine_test_configs import Config004
from .engine_test_configs import Config005
from .engine_test_configs import Config006
from .engine_test_configs import Config007
from .engine_test_configs import Config008
from .engine_test_configs import Config009
from .engine_test_configs import Config010
from .engine_test_configs import Config011, Config012
from .engine_test_configs import Config013, Config014
from .engine_test_configs import Config015, Config016, Config017, Config018
from .engine_test_configs import Config019, Config020, Config021, Config022
from .engine_test_configs import Config023, Config024, Config025, Config026
from .engine_test_configs import Config027
from .engine_test_configs import Config028
from .engine_test_configs import Config029
from .engine_test_configs import Config030
from .utils import EngineTester
from .utils import EngineTestConfig


class TestEngine:
    """Performs a system test on the engine

    See README for in depth details
    """

    @pytest.mark.parametrize("conf",
    #                         [Cls() for Cls in EngineTestConfig.subclasses])
                             #[Config001, Config002, Config003, Config004,
                             # Config005, Config006, Config007, Config008,
                             # Config009, Config010, Config011, Config012,
                             # Config013, Config014, Config015, Config016,
                             # Config017, Config018, Config019, Config020,
                             # Config021, Config022, Config023, Config024,
                             # Config025, Config026, 
                              [Config027, Config028, Config029, Config030])
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
