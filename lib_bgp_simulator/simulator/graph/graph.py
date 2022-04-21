from copy import deepcopy
from collections import defaultdict
from itertools import product
from multiprocessing import Pool

from lib_caida_collector import CaidaCollector


from ...scenarios import Scenario

from ...engine import BGPAS, SimulatorEngine


class Graph:
    #from .graph_writer import aggregate_and_write, get_graphs_to_write
    #from .graph_writer import _get_line, _write

    def __init__(self,
                 name,
                 *,
                 percent_adoptions,
                 scenarios,
                 subgraphs,
                 num_trials=1,
                 propagation_rounds=1):
        """Stores instance attributes"""

        self.name = name
        assert isinstance(percent_adoptions, tuple)
        self.percent_adoptions = percent_adoptions
        self.scenarios = scenarios
        # Validate that all scenarios have a unique graph label
        # We don't assert this in the scenario subclasses
        # Because really they only need to be unique per graph
        graph_labels = [x.graph_label for x in self.scenarios]
        msg = "Graph labels must be unique in Scenario subclass {graph_labels}"
        assert len(set(graph_labels)) == len(graph_labels), msg
        self.num_trials = num_trials
        # Why propagation rounds? Because some atk/def scenarios might require
        # More than one round of propagation
        self.propagation_rounds = propagation_rounds
        self.subgraphs = subgraphs
        assert subgraphs

    from .get_data_funcs import run
    from .get_data_funcs import _get_chunks
    from .get_data_funcs import _get_single_process_results
    from .get_data_funcs import _get_mp_results
    from .get_data_funcs import _run_chunk
    from .get_data_funcs import _aggregate_engine_run_data
