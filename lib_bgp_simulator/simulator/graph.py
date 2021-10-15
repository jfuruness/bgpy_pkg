from copy import deepcopy
from collections import defaultdict
import functools
from itertools import product
import logging
from multiprocessing import Pool
import random
import sys

from lib_caida_collector import CaidaCollector

from .engine_input import EngineInput
from .data_point import DataPoint
from .mp import MP
from .scenario import Scenario

from ..engine import BGPAS, SimulatorEngine


class Graph:
    from .graph_writer import aggregate_and_write, get_graphs_to_write
    from .graph_writer import _get_line, _write

    def __init__(self,
                 percent_adoptions=[0, 5, 10, 20, 30, 50, 75, 100],
                 adopt_as_classes=[],
                 EngineInputCls=None,
                 num_trials=1,
                 propagation_rounds=1,
                 BaseASCls=BGPAS,
                 profiler=None):
        assert isinstance(percent_adoptions, list)
        self.percent_adoptions = percent_adoptions
        self.adopt_as_classes = adopt_as_classes
        self.num_trials = num_trials
        # Why propagation rounds? Because some atk/def scenarios might require
        # More than one round of propagation
        self.propagation_rounds = propagation_rounds
        self.EngineInputCls = EngineInputCls
        self.BaseASCls = BaseASCls
        self.profiler = profiler


    def run(self,
            parse_cpus,
            _dir,
            caida_dir=None,
            mp_method=MP.SINGLE_PROCESS):
        self.data_points = defaultdict(list)
        self._dir = _dir
        self.caida_dir = caida_dir

        if mp_method == MP.SINGLE_PROCESS:
            results = self._get_single_process_results()
        elif mp_method == MP.MP:
            results = self._get_mp_results(parse_cpus)
            self._get_engine_and_save_subgraphs()
        elif mp_method == MP.RAY:
            results = self._get_ray_results(parse_cpus)
            self._get_engine_and_save_subgraphs()
        else:
            raise NotImplementedError

        for result in results:
            for data_point, trial_info_list in result.items():
                self.data_points[data_point].extend(trial_info_list)

        print("\nGraph complete")

######################################
# Multiprocessing/clustering methods #
######################################

    def _get_chunks(self, parse_cpus):
        """Not a generator since we need this for multiprocessing"""

        # https://stackoverflow.com/a/34032549/8903959
        percents_trials = list(product(self.percent_adoptions,
                                       list(range(self.num_trials))))

        # https://stackoverflow.com/a/2136090/8903959
        return [percents_trials[i::parse_cpus] for i in range(parse_cpus)]

    def _get_single_process_results(self):
        return [self._run_chunk(x) for x in self._get_chunks(1)]

    def _get_mp_results(self, parse_cpus):
        # Pool is much faster than ProcessPoolExecutor
        with Pool(parse_cpus) as pool:
            return pool.map(self._run_chunk, self._get_chunks(parse_cpus))

    def _get_ray_results(self, parse_cpus):
        assert "pypy" not in sys.executable, "Ray not compatible with pypy"
        import ray
        results = [ray.remote(self.__class__._run_chunk).remote(self, x)
                   for x in self._get_chunks(
                   int(ray.cluster_resources()["CPU"]))]
        return [ray.get(x) for x in results]

    def _run_chunk(self, percent_adopt_trials):
        # Engine is not picklable or dillable AT ALL, so do it here
        # Changing recursion depth does nothing
        # Making nothing a reference does nothing
        engine = self._get_engine_and_save_subgraphs()

        data_points = defaultdict(list)

        for percent_adopt, trial in percent_adopt_trials:
            engine_input = self.EngineInputCls(self.subgraphs,
                                               engine,
                                               percent_adopt)
            for ASCls in self.adopt_as_classes:
                print(f"{percent_adopt}% {ASCls.name}, #{trial}",
                      end="   " + "\r")
                # Deepcopy input to make sure input is fresh
                engine_input = deepcopy(engine_input)
                # Change AS Classes, seed announcements before propagation
                engine.setup(engine_input, self.BaseASCls, ASCls)

                for propagation_round in range(self.propagation_rounds):
                    # Generate the test
                    scenario = Scenario(trial=trial,
                                        engine=engine,
                                        engine_input=engine_input,
                                        profiler=self.profiler)
                    # Run test, remove reference to engine and return it
                    scenario.run(self.subgraphs, propagation_round)
                    # Get data point - just a frozen data class
                    # Just makes it easier to access properties later
                    dp = DataPoint(percent_adopt, ASCls, propagation_round)
                    # Append the test to all tests for that data point
                    data_points[dp].append(scenario)
                    engine_input.post_propagation_hook(engine, dp)
        return data_points

##########################
# Subgraph ASN functions #
##########################

    def _get_engine_and_save_subgraphs(self):
        # Done just to get subgraphs, change this later
        engine = CaidaCollector(BaseASCls=self.BaseASCls,
                                GraphCls=SimulatorEngine,
                                _dir=self.caida_dir,
                                _dir_exist_ok=True).run(tsv=False)
        self.subgraphs = self._get_subgraphs(engine)
        self._validate_subgraphs()

        return engine


    def _get_subgraphs(self, engine=None):
        """Returns all the subgraphs that you want to keep track of"""

        top_level = set(x.asn for x in engine if x.input_clique)
        stubs_and_mh = set([x.asn for x in engine if x.stub or x.multihomed])

        subgraphs = dict()
        # Remove sets to make keeping deterministic properties easier
        subgraphs["etc"] = set([x.asn for x in engine
                                if x.asn not in top_level
                                and x.asn not in stubs_and_mh])
        subgraphs["input_clique"] = top_level
        subgraphs["stubs_and_mh"] = stubs_and_mh
        return subgraphs

    def _validate_subgraphs(self):
        """Makes sure subgraphs are mutually exclusive and contain ASNs"""

        all_ases = []
        for subgraph_asns in self.subgraphs.values():
            msg = "Subgraphs must be sets for fast lookups"
            assert isinstance(subgraph_asns, set), msg
            all_ases.extend(subgraph_asns)
        for x in all_ases:
            assert isinstance(x, int), "Subgraph doesn't contain ASNs"

        msg = "subgraphs not mutually exclusive"
        assert len(all_ases) == len(set(all_ases)), msg

    @property
    def total_scenarios(self):
        total_scenarios = self.num_trials * len(self.percent_adoptions)
        total_scenarios *= len(self.adopt_as_classes)
        total_scenarios *= self.propagation_rounds
        return total_scenarios
