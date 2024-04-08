import gc
from itertools import product
from multiprocessing import cpu_count
from multiprocessing import Pool
from pathlib import Path
from typing import Optional, Union
import random
import os

from frozendict import frozendict

from bgpy.as_graphs.base import ASGraphConstructor, ASGraph
from bgpy.as_graphs.caida_as_graph import CAIDAASGraphConstructor


from .as_graph_analyzers import BaseASGraphAnalyzer, ASGraphAnalyzer
from .graph_factory import GraphFactory
from .metric_tracker import MetricTracker
from .metric_tracker.metric_key import MetricKey
from .scenarios import Scenario
from .scenarios import ScenarioConfig
from .scenarios import SubprefixHijack
from .utils import get_all_metric_keys

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import BaseSimulationEngine, SimulationEngine
from bgpy.simulation_engine import BGP
from bgpy.simulation_engine import BGPFull
from bgpy.simulation_engine import ROV


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
            [
                ScenarioConfig(
                    ScenarioCls=SubprefixHijack,
                    AdoptPolicyCls=ROV,
                    BasePolicyCls=BGP,
                )
            ]
        ),
        num_trials: int = 2,
        output_dir: Path = Path("/tmp/sims"),
        parse_cpus: int = cpu_count(),
        python_hash_seed: Optional[int] = None,
        ASGraphConstructorCls: type[ASGraphConstructor] = CAIDAASGraphConstructor,
        as_graph_constructor_kwargs=frozendict(
            {
                "as_graph_collector_kwargs": frozendict(
                    {
                        # dl_time: datetime(),
                        "cache_dir": Path("/tmp/as_graph_collector_cache"),
                    }
                ),
                "as_graph_kwargs": frozendict({"customer_cones": True}),
                "tsv_path": None,  # Path.home() / "Desktop" / "caida.tsv",
            }
        ),
        SimulationEngineCls: type[BaseSimulationEngine] = SimulationEngine,
        ASGraphAnalyzerCls: type[BaseASGraphAnalyzer] = ASGraphAnalyzer,
        MetricTrackerCls: type[MetricTracker] = MetricTracker,
        # Data plane tracking for traceback and MetricTrackerCls
        data_plane_tracking: bool = True,
        # Control plane trackign for traceback and MetricTrackerCls
        control_plane_tracking: bool = False,
        metric_keys: tuple[MetricKey, ...] = tuple(list(get_all_metric_keys())),
    ) -> None:
        """Downloads relationship data, runs simulation

        Graphs -> A list of graph classes
        graph_path: Where to store the graphs. Should be a .tar.gz file
        assert_pypy: Ensures you are using pypy if true
        mp_method: Multiprocessing method
        """

        self.percent_adoptions: tuple[Union[float, SpecialPercentAdoptions], ...] = (
            percent_adoptions
        )
        self.num_trials: int = num_trials
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parse_cpus: int = parse_cpus
        self.scenario_configs: tuple[ScenarioConfig, ...] = scenario_configs

        self.python_hash_seed: Optional[int] = python_hash_seed
        self._seed_random()

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        self.ASGraphConstructorCls: type[ASGraphConstructor] = ASGraphConstructorCls
        self.as_graph_constructor_kwargs = as_graph_constructor_kwargs
        self.ASGraphConstructorCls(**as_graph_constructor_kwargs).run()

        self.SimulationEngineCls: type[BaseSimulationEngine] = SimulationEngineCls

        self.ASGraphAnalyzerCls: type[BaseASGraphAnalyzer] = ASGraphAnalyzerCls
        self.MetricTrackerCls: type[MetricTracker] = MetricTrackerCls

        self.data_plane_tracking: bool = data_plane_tracking
        self.control_plane_tracking: bool = control_plane_tracking

        self._validate_scenario_configs()

        self.metric_keys: tuple[MetricKey, ...] = metric_keys

        for scenario_config in self.scenario_configs:
            if isinstance(scenario_config.AdoptPolicyCls, BGPFull) and not isinstance(
                scenario_config.BasePolicyCls, BGPFull
            ):
                raise Exception(
                    "You have an AdoptPolicyCls inheriting from BGPFull "
                    "but your BasePolicyCls is not. You may want to pass in "
                    "BasePolicyCls=BGPFull to your scenario_config"
                )

    def _validate_scenario_configs(self) -> None:
        """validates that the scenario configs

        adopt and base policies don't overlap with the hardcoded asns

        If they do, setting and unsetting from scenario to scenario will fail

        If they do overlap, just make a subclass of the Policy you are using
        in the hardcoded ASNs
        """

        adopt_and_base_policies = set()
        for scenario_config in self.scenario_configs:
            adopt_and_base_policies.add(scenario_config.AdoptPolicyCls)
            adopt_and_base_policies.add(scenario_config.BasePolicyCls)

        hardcoded_asn_policies = set()
        for scenario_config in self.scenario_configs:
            for value in scenario_config.hardcoded_asn_cls_dict:
                hardcoded_asn_policies.add(value)

        diff = adopt_and_base_policies.intersection(hardcoded_asn_policies)

        msg = (
            "Can't have AdoptPolicyCls or BasePolicyCls be in the harcoded_asn_cls_dict"
            " since this will not be set properly when comparing multiple scenarios"
            " instead, for the hardcoded_asn_cls_dict, take the subclass of your policy"
            " and use that instead"
        )
        assert len(diff) == 0, msg

    def run(
        self,
        GraphFactoryCls: Optional[type[GraphFactory]] = GraphFactory,
        graph_factory_kwargs=None,
    ) -> None:
        """Runs the simulation and write the data"""

        metric_tracker = self._get_data()
        metric_tracker.write_data(csv_path=self.csv_path, pickle_path=self.pickle_path)
        self._graph_data(GraphFactoryCls, graph_factory_kwargs)
        # This object holds a lot of memory, good to get rid of it
        del metric_tracker
        gc.collect()

    def _seed_random(self, seed_suffix: str = "") -> None:
        """Seeds randomness"""

        if self.python_hash_seed is not None:
            msg = (
                f"You've set the python_hash_seed to {self.python_hash_seed}, but "
                "the simulations aren't deterministic unless you also set the "
                "PYTHONHASHSEED in the env, such as with \n"
                f"export PYTHONHASHSEED={self.python_hash_seed}"
            )
            if os.environ.get("PYTHONHASHSEED") != str(self.python_hash_seed):
                raise Exception(msg)
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
        constructor_kwargs = dict(self.as_graph_constructor_kwargs)
        constructor_kwargs["tsv_path"] = None
        as_graph: ASGraph = self.ASGraphConstructorCls(**constructor_kwargs).run()
        engine = self.SimulationEngineCls(
            as_graph,
            cached_as_graph_tsv_path=self.as_graph_constructor_kwargs.get("tsv_path"),
        )

        metric_tracker = self.MetricTrackerCls(metric_keys=self.metric_keys)

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
                    preprocess_anns_func=scenario_config.preprocess_anns_func,
                )

                self._print_progress(percent_adopt, scenario, trial)

                # Change AS Classes, seed announcements before propagation
                scenario.setup_engine(engine, prev_scenario)
                # For each round of propagation run the engine
                for propagation_round in range(scenario_config.propagation_rounds):
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
        trial: int,
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
        engine: BaseSimulationEngine,
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
            propagation_round=propagation_round,
        )

        self._collect_engine_run_data(
            engine,
            percent_adopt,
            trial,
            scenario,
            propagation_round,
            metric_tracker,
        )

        # By default, this is a no op
        scenario.post_propagation_hook(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            propagation_round=propagation_round,
        )

    def _collect_engine_run_data(
        self,
        engine: SimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        metric_tracker: MetricTracker,
    ) -> dict[int, dict[int, int]]:
        # Save all engine run info
        # The reason we aggregate info right now, instead of saving
        # the engine and doing it later, is because doing it all
        # in RAM is MUCH faster, and speed is important
        outcomes = self.ASGraphAnalyzerCls(
            engine=engine,
            scenario=scenario,
            data_plane_tracking=self.data_plane_tracking,
            control_plane_tracking=self.control_plane_tracking,
        ).analyze()

        metric_tracker.track_trial_metrics(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            scenario=scenario,
            propagation_round=propagation_round,
            outcomes=outcomes,
        )
        return outcomes

    ######################
    # Data Writing Funcs #
    ######################

    @property
    def csv_path(self) -> Path:
        return self.output_dir / "data.csv"

    @property
    def pickle_path(self) -> Path:
        return self.output_dir / "data.pickle"

    #######################
    # Graph Writing Funcs #
    #######################

    def _graph_data(
        self,
        GraphFactoryCls: Optional[type[GraphFactory]] = GraphFactory,
        kwargs=None,
    ) -> None:
        """Generates some default graphs"""

        if kwargs is None:
            kwargs = dict()
        # Set defaults for kwargs
        kwargs["pickle_path"] = kwargs.pop("pickle_path", self.pickle_path)
        kwargs["graph_dir"] = kwargs.pop("graph_dir", self.output_dir / "graphs")
        kwargs["metric_keys"] = kwargs.pop("metric_keys", self.metric_keys)
        if GraphFactoryCls:
            GraphFactoryCls(**kwargs).generate_graphs()
            print(f"\nWrote graphs to {kwargs['graph_dir']}")

    @property
    def graph_output_dir(self) -> Path:
        return self.output_dir / "graphs"
