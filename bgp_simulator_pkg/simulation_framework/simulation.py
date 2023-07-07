import csv
from itertools import product
from multiprocessing import cpu_count
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Optional, Union
import random
import os

from bgp_simulator_pkg.caida_collector import CaidaCollector

from .graph_analyzer import GraphAnalyzer
from .metric_tracker import MetricTracker
from .scenarios import Scenario
from .scenarios import ScenarioConfig
from .scenarios import SubprefixHijack

from bgp_simulator_pkg.enums import SpecialPercentAdoptions
from bgp_simulator_pkg.simulation_engine import BGPSimpleAS
from bgp_simulator_pkg.simulation_engine import SimulationEngine
from bgp_simulator_pkg.simulation_engine import ROVSimpleAS


class Simulation:
    """Runs simulations for BGP attack/defend scenarios"""

    def __init__(
        self,
        percent_adoptions: tuple[Union[float, SpecialPercentAdoptions], ...] = (
            0.1,
            0.5,
            0.8,
        ),
        scenario_configs: tuple[ScenarioConfig, ...] = tuple(
            [ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptASCls=ROVSimpleAS)]
        ),
        num_trials: int = 2,
        propagation_rounds: int = 1,
        output_dir: Path = Path("/tmp/sims"),
        parse_cpus: int = cpu_count(),
        python_hash_seed: Optional[int] = None,
        engine_kwargs: Optional[dict[Any, Any]] = None,
        GraphAnalyzerCls: type[GraphAnalyzer] = GraphAnalyzer,
        MetricTrackerCls: type[MetricTracker] = MetricTracker,
    ) -> None:
        """Downloads relationship data, runs simulation

        Graphs -> A list of graph classes
        graph_path: Where to store the graphs. Should be a .tar.gz file
        assert_pypy: Ensures you are using pypy if true
        mp_method: Multiprocessing method
        """

        self.percent_adoptions: tuple[
            Union[float, SpecialPercentAdoptions], ...
        ] = percent_adoptions
        self.num_trials: int = num_trials
        self.propagation_rounds: int = propagation_rounds
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parse_cpus: int = parse_cpus
        self.scenario_configs: tuple[ScenarioConfig, ...] = scenario_configs

        msg = ("Please add a unique_data_label to scenario configs. "
               "These are used for data storage as keys, and currently aren't"
               " unique enough")
        labels = [x.unique_data_label for x in self.scenario_configs]
        assert len(labels) == len(set(labels)), msg

        self.python_hash_seed: Optional[int] = python_hash_seed
        self._seed_random()

        if engine_kwargs:
            self.engine_kwargs: dict[Any, Any] = engine_kwargs
        else:
            self.engine_kwargs = {
                "BaseASCls": BGPSimpleAS,
                "GraphCls": SimulationEngine,
            }
        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector().run()

        self.GraphAnalyzerCls = GraphAnalyzerCls
        self.MetricTrackerCls = MetricTrackerCls

    def run(self):
        """Runs the simulation and write the data"""

        metric_tracker = self._get_data()
        metric_tracker.write_csv(self.data_output_path)
        self._graph_data()

    def _seed_random(self, seed_suffix: str = "") -> None:
        """Seeds randomness"""

        if self.python_hash_seed is not None:
            msg = "Not deterministic unless you also set PYTHONHASHSEED in the env"
            assert os.environ.get("PYTHONHASHSEED") == str(self.python_hash_seed), msg

            random.seed(str(self.python_hash_seed) + seed_suffix)

    def _get_data(self):
        """Runs trials for graph and aggregates data"""

        # Single process
        if self.parse_cpus == 1:
            # Results are a list of lists of metric trackers that we then sum
            return sum(
                self._get_single_process_results(), start=self.MetricTrackerCls()
            )
        # Multiprocess
        else:
            # Results are a list of lists of metric trackers that we then sum
            return sum(
                self._get_mp_results(self.parse_cpus), start=self.MetricTrackerCls()
            )

    ###########################
    # Multiprocessing Methods #
    ###########################

    def _get_chunks(
        self, cpus: int
    ) -> list[list[tuple[Union[float, SpecialPercentAdoptions], int]]]:
        """Returns chunks of trial inputs based on number of CPUs running

        Not a generator since we need this for multiprocessing

        We also don't multiprocess one by one because the start up cost of
        each process is huge (since each process must generate it's own engine
        ) so we must divy up the work beforehand
        """

        # https://stackoverflow.com/a/34032549/8903959
        combos = product(self.percent_adoptions, list(range(self.num_trials)))
        percents_trials = [tuple(x) for x in combos]

        # https://stackoverflow.com/a/2136090/8903959
        # mypy can't seem to handle these types?
        return [percents_trials[i::cpus] for i in range(cpus)]  # type: ignore

    def _get_single_process_results(self) -> list[MetricTracker]:
        """Get all results when using single processing"""

        return [self._run_chunk(i, x) for i, x in enumerate(self._get_chunks(1))]

    def _get_mp_results(self, parse_cpus: int) -> list[MetricTracker]:
        """Get results from multiprocessing"""

        # Pool is much faster than ProcessPoolExecutor
        with Pool(parse_cpus) as p:
            return p.starmap(self._run_chunk, enumerate(self._get_chunks(parse_cpus)))

    ############################
    # Data Aggregation Methods #
    ############################

    def _run_chunk(
        self,
        chunk_id: int,
        percent_adopt_trials: list[tuple[Union[float, SpecialPercentAdoptions], int]],
    ) -> MetricTracker:
        """Runs a chunk of trial inputs"""

        # Must also seed randomness here since we don't want multiproc to be the same
        self._seed_random(seed_suffix=str(chunk_id))

        # Engine is not picklable or dillable AT ALL, so do it here
        # (after the multiprocess process has started)
        # Changing recursion depth does nothing
        # Making nothing a reference does nothing
        engine = CaidaCollector(**self.engine_kwargs.copy()).run(tsv_path=None)

        metric_tracker = self.MetricTrackerCls()

        prev_scenario = None

        for percent_adopt, trial in percent_adopt_trials:
            for scenario_config in self.scenario_configs:

                # Create the scenario for this trial
                assert scenario_config.ScenarioCls, "ScenarioCls is None"
                scenario = scenario_config.ScenarioCls(
                    scenario_config=scenario_config,
                    percent_adoption=percent_adopt,
                    engine=engine,
                    prev_scenario=prev_scenario,
                )

                self._print_progress(percent_adopt, scenario, trial)

                # Change AS Classes, seed announcements before propagation
                scenario.setup_engine(engine, prev_scenario)

                # For each round of propagation run the engine
                for propagation_round in range(self.propagation_rounds):
                    self._single_engine_run(
                        engine=engine,
                        percent_adopt=percent_adopt,
                        trial=trial,
                        scenario=scenario,
                        propagation_round=propagation_round,
                        metric_tracker=metric_tracker,
                    )
                prev_scenario = scenario
            # Reset scenario for next round of trials
            prev_scenario = None

        return metric_tracker

    def _print_progress(
        self,
        percent_adopt: Union[float | SpecialPercentAdoptions],
        scenario: Scenario,
        trial: int
    ) -> None:
        """Printing progress"""

        if not isinstance(percent_adopt, (float, SpecialPercentAdoptions)):
            raise Exception("Percent Adoptions not float or SpecialPercentAdoptions")
        elif float(percent_adopt) > 1:
            raise Exception("Percent Adoptions must be decimals less than 1")
        else:
            name = scenario.__class__.__name__
            print(f"{float(percent_adopt) * 100}% {name} #{trial}", end=" " * 10 + "\r")

    def _single_engine_run(
        self,
        *,
        engine: SimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        metric_tracker: MetricTracker,
    ) -> None:
        """Single engine run"""

        # Run the engine
        engine.run(propagation_round=propagation_round, scenario=scenario)

        # Pre-aggregation Hook
        scenario.pre_aggregation_hook(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            propagation_round=propagation_round
        )

        # Save all engine run info
        # The reason we aggregate info right now, instead of saving
        # the engine and doing it later, is because doing it all
        # in RAM is MUCH faster, and speed is important
        outcomes = self.GraphAnalyzerCls(engine=engine, scenario=scenario).analyze()
        metric_tracker.track_trial_metrics(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            scenario=scenario,
            propagation_round=propagation_round,
            outcomes=outcomes
        )

        # By default, this is a no op
        scenario.post_propagation_hook(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            propagation_round=propagation_round,
        )

######################
# Data Writing Funcs #
######################

    @property
    def data_output_path(self) -> Path:
        return self.output_dir / "data.csv"

#######################
# Graph Writing Funcs #
#######################

    def _graph_data(self) -> None:
        """Generates some default graphs"""
        print("TODO")
        # Write archive to temp dir then copy it to output path
        #             make_archive(self.output_path, "zip", tmp_dir)
        # print(f"\nWrote graphs to {self.output_path}.zip")

    @property
    def graph_output_dir(self) -> Path:
        return self.output_dir / "graphs"
