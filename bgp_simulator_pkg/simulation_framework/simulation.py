from copy import deepcopy
from itertools import product
import json
from multiprocessing import Pool
from pathlib import Path
from shutil import make_archive
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple, Union
import random
import os

from caida_collector_pkg import CaidaCollector

from .scenarios import Scenario
from .scenarios import SubprefixHijack
from .subgraphs import Subgraph
from ..enums import SpecialPercentAdoptions
from ..simulation_engine import BGPSimpleAS
from ..simulation_engine import SimulationEngine
from ..simulation_engine import ROVSimpleAS


class Simulation:
    """Runs simulations for BGP attack/defend scenarios"""

    def __init__(self,
                 percent_adoptions: Tuple[
                    Union[float, SpecialPercentAdoptions], ...] = (
                        .05, .1, .3, .5, .8),
                 scenarios: Tuple[Scenario, ...] = tuple(
                    [SubprefixHijack(AdoptASCls=x)  # type: ignore
                     for x in [ROVSimpleAS]]
                    ),
                 subgraphs: Optional[Tuple[Subgraph, ...]] = None,
                 num_trials: int = 2,
                 propagation_rounds: int = 1,
                 output_path: Path = Path("/tmp/graphs"),
                 parse_cpus: int = 8,
                 python_hash_seed: Optional[int] = None):
        """Downloads relationship data, runs simulation

        Graphs -> A list of graph classes
        graph_path: Where to store the graphs. Should be a .tar.gz file
        assert_pypy: Ensures you are using pypy if true
        mp_method: Multiprocessing method
        """

        if subgraphs:
            self.subgraphs: Tuple[Subgraph, ...] = subgraphs
        else:
            self.subgraphs = tuple([
                Cls() for Cls in
                Subgraph.subclasses if Cls.name])

        self.percent_adoptions: Tuple[Union[float,
                                            SpecialPercentAdoptions],
                                      ...] = percent_adoptions
        self.num_trials: int = num_trials
        self.propagation_rounds: int = propagation_rounds
        self.output_path: Path = output_path
        self.parse_cpus: int = parse_cpus
        self.scenarios: Tuple[Scenario, ...] = scenarios
        self.python_hash_seed = python_hash_seed
        # All scenarios must have a uni que graph label
        labels = [x.graph_label for x in self.scenarios]
        assert len(labels) == len(set(labels)), "Scenario labels not unique"

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector().run()

    def run(self):
        """Runs the simulation and write the data"""

        self._get_data()
        self._write_data()

    def _write_data(self):
        """Writes subgraphs in graph_dir"""

        # init JSON and temporary directory
        json_data = dict()
        with TemporaryDirectory() as tmp_dir:
            # Write subgraph and add data to the JSON
            for subgraph in self.subgraphs:
                subgraph.write_graphs(Path(tmp_dir))
                json_data[subgraph.name] = subgraph.data
            # Save the JSON
            with (Path(tmp_dir) / "results.json").open("w") as f:
                json.dump(json_data, f, indent=4)

            # Zip the data
            make_archive(self.output_path, "zip", tmp_dir)  # type: ignore
            print(f"\nWrote graphs to {self.output_path}.zip")

    def _get_data(self):
        """Runs trials for graph and aggregates data"""

        # Single process
        if self.parse_cpus == 1:
            # Results are a list of lists of subgraphs
            results = self._get_single_process_results()
        # Multiprocess
        else:
            # Results are a list of lists of subgraphs
            results = self._get_mp_results(self.parse_cpus)

        # Results is a list of lists of subgraphs
        # This joins all results from all trials
        for result_subgraphs in results:
            for self_subgraph, result_subgraph in zip(self.subgraphs,
                                                      result_subgraphs):
                # Merges the trial subgraph into this subgraph
                self_subgraph.add_trial_info(result_subgraph)

    def _check_python_hash_seed(self, set_random_seed: bool = False):
        """Checks that the python_hash_seed is the same
        as environment variable PYTHONHASHSEED
        set_random_seed: bool:  set the random.seed() with
        python_hash_seed value.
        """
        # Check if python_hash_seed is set
        if self.python_hash_seed is not None:
            # Check if PYTHONHASHSEED environment variable
            # is set properly
            env_var = os.environ.get('PYTHONHASHSEED')
            assert env_var and env_var == str(self.python_hash_seed), "" \
                "If python_hash_seed is set then " \
                "'PYTHONHASHSEED' environement needs to be set as the " \
                "same value as python_hash_seed"
            if set_random_seed:
                # Set random seed
                random.seed(self.python_hash_seed)

###########################
# Multiprocessing Methods #
###########################

    def _get_chunks(self,
                    parse_cpus: int
                    ) -> List[List[Tuple[Union[float, SpecialPercentAdoptions],
                                         int]]]:
        """Returns chunks of trial inputs based on number of CPUs running

        Not a generator since we need this for multiprocessing

        We also don't multiprocess one by one because the start up cost of
        each process is huge (since each process must generate it's own engine
        ) so we must divy up the work beforehand
        """

        # https://stackoverflow.com/a/34032549/8903959
        percents_trials = [tuple(x) for x in
                           product(self.percent_adoptions,
                                   list(range(self.num_trials)))]

        # https://stackoverflow.com/a/2136090/8903959
        # mypy can't seem to handle these types?
        return [percents_trials[i::parse_cpus]  # type: ignore
                for i in range(parse_cpus)]

    def _get_single_process_results(self) -> List[Tuple[Subgraph, ...]]:
        """Get all results when using single processing"""

        # Check if the python_hash_seed is set properly
        self._check_python_hash_seed(set_random_seed=True)
        return [self._run_chunk(chunk_id, x, single_proc=True)
                for chunk_id, x in enumerate(self._get_chunks(1))]

    def _get_mp_results(self, parse_cpus: int) -> List[Tuple[Subgraph, ...]]:
        """Get results from multiprocessing"""

        # Check if the python_hash_seed is set properly
        self._check_python_hash_seed()
        # Pool is much faster than ProcessPoolExecutor
        with Pool(parse_cpus) as pool:
            return pool.starmap(self._run_chunk,  # type: ignore
                                enumerate(self._get_chunks(parse_cpus)))

############################
# Data Aggregation Methods #
############################

    def _run_chunk(self,
                   chunk_id: int,
                   percent_adopt_trials: List[Tuple[Union[float,
                                                    SpecialPercentAdoptions],
                                                    int]],
                   # MUST leave as false. _get_mp_results depends on this
                   # This should be fixed and this comment deleted
                   single_proc: bool = False
                   ) -> Tuple[Subgraph, ...]:
        """Runs a chunk of trial inputs"""

        # Check to enable deterministic multiprocess runs
        if self.python_hash_seed is not None and self.parse_cpus > 1:
            random.seed(chunk_id)

        # Engine is not picklable or dillable AT ALL, so do it here
        # (after the multiprocess process has started)
        # Changing recursion depth does nothing
        # Making nothing a reference does nothing
        engine = CaidaCollector(BaseASCls=BGPSimpleAS,
                                GraphCls=SimulationEngine,
                                ).run(tsv_path=None)
        # Must deepcopy here to have the same behavior between single
        # And multiprocessing
        if single_proc:
            subgraphs = deepcopy(self.subgraphs)
        else:
            subgraphs = self.subgraphs

        prev_scenario = None

        for percent_adopt, trial in percent_adopt_trials:
            for scenario in self.scenarios:

                # Deep copy scenario to ensure it's fresh
                # Since certain things like announcements change round to round
                scenario = deepcopy(scenario)

                if isinstance(percent_adopt, float):
                    print(f"{percent_adopt * 100}% "
                          f"{scenario.graph_label}, "
                          f"#{trial}",
                          end="                             " + "\r")
                elif isinstance(percent_adopt, SpecialPercentAdoptions):
                    print(f"{percent_adopt.value * 100}% "
                          f"{scenario.graph_label}, "
                          f"#{trial}",
                          end="                             " + "\r")
                elif percent_adopt > 1:  # type: ignore
                    raise Exception("Percent adoptions must be decimals <1")
                else:
                    raise NotImplementedError("Invalid percent adoptions")

                # Change AS Classes, seed announcements before propagation
                scenario.setup_engine(engine, percent_adopt, prev_scenario)

                for propagation_round in range(self.propagation_rounds):
                    # Run the engine
                    engine.run(propagation_round=propagation_round,
                               scenario=scenario)

                    kwargs = {"engine": engine,
                              "percent_adopt": percent_adopt,
                              "trial": trial,
                              "scenario": scenario,
                              "propagation_round": propagation_round}

                    # Pre-aggregation Hook
                    scenario.pre_aggregation_hook(**kwargs)

                    # Save all engine run info
                    # The reason we aggregate info right now, instead of saving
                    # the engine and doing it later, is because doing it all
                    # in RAM is MUCH faster, and speed is important
                    self._aggregate_engine_run_data(subgraphs, **kwargs)

                    # By default, this is a no op
                    scenario.post_propagation_hook(**kwargs)
                prev_scenario = scenario
            # Reset scenario for next round of trials
            prev_scenario = None
        return subgraphs

    def _aggregate_engine_run_data(self,
                                   subgraphs: Tuple[Subgraph, ...],
                                   **kwargs):
        """For each subgraph, aggregate data

        Some data aggregation is shared to speed up runs
        For example, traceback might be useful across
        Multiple subgraphs
        """

        shared_data: Dict[Any, Any] = dict()
        for subgraph in subgraphs:
            subgraph.aggregate_engine_run_data(shared_data, **kwargs)
