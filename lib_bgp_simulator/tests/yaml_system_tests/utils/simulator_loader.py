from lib_caida_collector import CaidaCollector
from lib_bgp_simulator import Simulator, Graph, ROVAS, SubprefixHijack, BGPAS, SimulatorEngine, YamlAbleEnum
from datetime import datetime
from pathlib import Path
# YAML STUFF
from yamlable import YamlCodec
from typing import Type, Any, Iterable, Tuple

from yaml import SafeLoader

# https://stackoverflow.com/a/39554610/8903959
class SimulatorLoader(SafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))

SimulatorLoader.add_constructor(u'tag:yaml.org,2002:python/tuple',
                                SimulatorLoader.construct_python_tuple)
