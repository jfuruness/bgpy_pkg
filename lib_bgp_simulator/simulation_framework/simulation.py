from copy import deepcopy
from itertools import product
import json
from multiprocessing import Pool
from pathlib import Path
from shutil import make_archive
from tempfile import TemporaryDirectory
from typing import Iterator


from lib_caida_collector import CaidaCollector

from .scenarios import Scenario
from .scenarios import SubprefixHijack
from .subgraphs import Subgraph
from .subgraphs import AttackerSuccessAdoptingEtcSubgraph
from .subgraphs import AttackerSuccessAdoptingInputCliqueSubgraph
from .subgraphs import AttackerSuccessAdoptingStubsAndMHSubgraph
from .subgraphs import AttackerSuccessNonAdoptingEtcSubgraph
from .subgraphs import AttackerSuccessNonAdoptingInputCliqueSubgraph
from .subgraphs import AttackerSuccessNonAdoptingStubsAndMHSubgraph
from .subgraphs import AttackerSuccessAllSubgraph
from ..simulation_engine import BGPSimpleAS
from ..simulation_engine import SimulationEngine
from ..simulation_engine import ROVSimpleAS


class Simulation:
    """Runs simulations for BGP attack/defend scenarios"""

    def __init__(
            self,
            percent_adoptions=(.05, .1, .3, .5, .8),
            scenarios=[SubprefixHijack(AdoptASCls=x)  # type: ignore
                       for x in [ROVSimpleAS]],
            subgraphs=[
              AttackerSuccessAdoptingEtcSubgraph(),
              AttackerSuccessAdoptingInputCliqueSubgraph(),
              AttackerSuccessAdoptingStubsAndMHSubgraph(),
              AttackerSuccessNonAdoptingEtcSubgraph(),
              AttackerSuccessNonAdoptingInputCliqueSubgraph(),
              AttackerSuccessNonAdoptingStubsAndMHSubgraph(),
              AttackerSuccessAllSubgraph()],
            num_trials: int = 1,
            propagation_rounds: int = 1,
            output_path: Path = Path("/tmp/graphs"),
            parse_cpus: int = 1
            ):
        """Downloads relationship data, runs simulation

        Graphs -> A list of graph classes
        graph_path: Where to store the graphs. Should be a .tar.gz file
        assert_pypy: Ensures you are using pypy if true
        mp_method: Multiprocessing method
        """

        self.percent_adoptions: Iterator[int] = percent_adoptions
        self.scenarios: Iterator[Scenario] = scenarios
        self.subgraphs: Iterator[Subgraph] = subgraphs
        self.num_trials: int = num_trials
        self.propagation_rounds: int = propagation_rounds
        self.output_path: Path = output_path
        self.parse_cpus: int = parse_cpus

        # All scenarios must have a uni que graph label
        labels = [x.graph_label for x in self.scenarios]
        assert len(labels) == len(set(labels)), "Scenario labels not unique"

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector().run()

    def run(self) -> None:
        """Runs the simulation and write the data"""

        self._get_data()
        self._write_data()

    def _write_data(self) -> None:
        """Writes subgraphs in graph_dir"""

        # init JSON and temporary directory
        json_data: dict = dict()
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

    def _get_data(self) -> None:
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

###########################
# Multiprocessing Methods #
###########################

    def _get_chunks(self, parse_cpus: int):
        """Returns chunks of trial inputs based on number of CPUs running

        Not a generator since we need this for multiprocessing

        We also don't multiprocess one by one because the start up cost of
        each process is huge (since each process must generate it's own engine
        ) so we must divy up the work beforehand
        """

        # https://stackoverflow.com/a/34032549/8903959
        percents_trials = list(product(self.percent_adoptions,
                                       list(range(self.num_trials))))

        # https://stackoverflow.com/a/2136090/8903959
        return [percents_trials[i::parse_cpus] for i in range(parse_cpus)]

    def _get_single_process_results(self):
        """Get all results when using single processing"""

        return [self._run_chunk(x, single_proc=True)
                for x in self._get_chunks(1)]

    def _get_mp_results(self, parse_cpus: int):
        """Get results from multiprocessing"""

        # Pool is much faster than ProcessPoolExecutor
        with Pool(parse_cpus) as pool:
            return pool.map(self._run_chunk, self._get_chunks(parse_cpus))

############################
# Data Aggregation Methods #
############################

    def _run_chunk(self,
                   percent_adopt_trials,
                   single_proc=False) -> Iterator[Subgraph]:
        """Runs a chunk of trial inputs"""

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

                print(
                    f"{percent_adopt * 100}% {scenario.graph_label}, #{trial}",
                    end="                             " + "\r")

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
                    # Save all engine run info
                    # The reason we aggregate info right now, instead of saving
                    # the engine and doing it later, is because doing it all
                    # in RAM is MUCH faster, and speed is important
                    self._aggregate_engine_run_data(subgraphs, **kwargs)

                    # By default, this is a no op
                    scenario.post_propagation_hook(**kwargs)
            # Reset scenario for next round of trials
            prev_scenario = None
        return subgraphs

    def _aggregate_engine_run_data(self,
                                   subgraphs: Iterator[Subgraph],
                                   **kwargs) -> None:
        """For each subgraph, aggregate data

        Some data aggregation is shared to speed up runs
        For example, traceback might be useful across
        Multiple subgraphs
        """

        shared_data: dict = dict()
        for subgraph in subgraphs:
            subgraph.aggregate_engine_run_data(shared_data, **kwargs)
