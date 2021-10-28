from .conftest import pytest_addoption

# Graphs
from .graphs import GraphInfo
from .graphs import Graph001
from .graphs import Graph002
from .graphs import Graph003
from .graphs import Graph004
from .graphs import Graph005
from .graphs import Graph006
from .graphs import Graph007
from .graphs import Graph008
from .graphs import Graph009

# System tests that may be useful elsewhere (not YAML)
from .system_tests import test_sim_inputs

# Classes to run/write tests
from .utils import BaseGraphSystemTester
from .utils import YamlSystemTestRunner

# Yaml system tests that can be used again elsewhere
from .yaml_system_tests import BaseHiddenHijackTester
from .yaml_system_tests import BaseBGPPropTester
from .yaml_system_tests import BaseFig2Tester
from .yaml_system_tests import BaseNonRoutedSuperprefixTester
from .yaml_system_tests import BaseNonRoutedPrefixTester
