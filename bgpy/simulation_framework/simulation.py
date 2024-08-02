from copy import deepcopy
import gc
from multiprocessing import cpu_count
from multiprocessing import Pool
import os
from pathlib import Path
import random
import shutil
from tempfile import TemporaryDirectory
import time
from typing import Iterator, Optional, Union

from frozendict import frozendict
from tqdm import tqdm

from bgpy.as_graphs.base import ASGraphConstructor, ASGraph
from bgpy.as_graphs.caida_as_graph import CAIDAASGraphConstructor


from .as_graph_analyzers import BaseASGraphAnalyzer, ASGraphAnalyzer
from .graphing import GraphFactory
from .graph_data_aggregator import GraphDataAggregator, GraphCategory
from .scenarios import Scenario
from .scenarios import ScenarioConfig
from .scenarios import SubprefixHijack
from .utils import get_all_graph_categories

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
        parse_cpus: int = max(cpu_count() - 1, 1),
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
        GraphDataAggregatorCls: type[GraphDataAggregator] = GraphDataAggregator,
        # Data plane tracking for traceback and GraphDataAggregatorCls
        data_plane_tracking: bool = True,
        # Control plane trackign for traceback and GraphDataAggregatorCls
        control_plane_tracking: bool = False,
        graph_categories: tuple[GraphCategory, ...] = tuple(
            list(get_all_graph_categories())
        ),
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
        self.GraphDataAggregatorCls: type[GraphDataAggregator] = GraphDataAggregatorCls

        self.data_plane_tracking: bool = data_plane_tracking
        self.control_plane_tracking: bool = control_plane_tracking

        self.graph_categories: tuple[GraphCategory, ...] = graph_categories

        scenario_labels = list()
        for scenario_config in self.scenario_configs:
            scenario_labels.append(scenario_config.scenario_label)
            if isinstance(scenario_config.AdoptPolicyCls, BGPFull) and not isinstance(
                scenario_config.BasePolicyCls, BGPFull
            ):
                raise Exception(
                    "You have an AdoptPolicyCls inheriting from BGPFull "
                    "but your BasePolicyCls is not. You may want to pass in "
                    "BasePolicyCls=BGPFull to your scenario_config"
                )

        if len(set(scenario_labels)) != len(scenario_labels):
            raise ValueError(
                "Each ScenarioConfig uses a scenario_label when aggregating results "
                "which by default is set to the AdoptPolicyCls's name attribute. "
                "Since you have two ScenarioConfig's with the same label, metrics "
                "won't aggregate properly. Please pass in a scenario_label= with a "
                "unique label name to your config"
            )

        # Can't delete this since it gets deleted in multiprocessing for some reason
        # NOTE: Once pypy gets to 3.12, just pass delete=False to this
        with TemporaryDirectory() as tmp_dir:
            tmp_dir_str = tmp_dir
        self._tqdm_tracking_dir: Path = Path(tmp_dir_str)
        self._tqdm_tracking_dir.mkdir(parents=True)

    def run(
        self,
        GraphFactoryCls: Optional[type[GraphFactory]] = GraphFactory,
        graph_factory_kwargs=None,
    ) -> None:
        """Runs the simulation and write the data"""

        graph_data_aggregator = self._get_data()
        graph_data_aggregator.write_data(
            csv_path=self.csv_path, pickle_path=self.pickle_path
        )
        self._graph_data(GraphFactoryCls, graph_factory_kwargs)
        # This object holds a lot of memory, good to get rid of it
        del graph_data_aggregator
        gc.collect()
        shutil.rmtree(self._tqdm_tracking_dir)

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
                self._get_single_process_results(), start=self.GraphDataAggregatorCls()
            )
        # Multiprocess
        else:
            # Results are a list of lists of metric trackers that we then sum
            return sum(self._get_mp_results(), start=self.GraphDataAggregatorCls())

    ###########################
    # Multiprocessing Methods #
    ###########################

    def _get_chunks(self, cpus: int) -> list[list[int]]:
        """Returns chunks of trial inputs based on number of CPUs running

        Not a generator since we need this for multiprocessing

        We also don't multiprocess one by one because the start up cost of
        each process is huge (since each process must generate it's own engine
        ) so we must divy up the work beforehand
        """

        trials_list = list(range(self.num_trials))
        return [trials_list[i::cpus] for i in range(cpus)]

    def _get_single_process_results(self) -> list[GraphDataAggregator]:
        """Get all results when using single processing"""

        return [self._run_chunk(i, x) for i, x in enumerate(self._get_chunks(1))]

    def _get_mp_results(self) -> list[GraphDataAggregator]:
        """Get results from multiprocessing

        Previously used starmap, but now we have tqdm
        """

        # Pool is much faster than ProcessPoolExecutor
        with Pool(self.parse_cpus) as p:
            # return p.starmap(self._run_chunk, enumerate(self._get_chunks(parse_cpus)))
            chunks = self._get_chunks(self.parse_cpus)
            desc = f"Simulating {self.output_dir.name}"
            with tqdm(total=sum(len(x) for x in chunks), desc=desc) as pbar:
                tasks = [p.apply_async(self._run_chunk, x) for x in enumerate(chunks)]
                completed = []  # type: ignore
                while tasks:
                    completed, tasks = self._get_completed_and_tasks(completed, tasks)
                    self._update_tqdm_progress_bar(pbar)
                    time.sleep(0.5)
        return completed

    def _get_completed_and_tasks(self, completed, tasks):
        """Moves completed tasks into completed"""
        new_tasks = list()
        for task in tasks:
            if task.ready():
                completed.append(task.get())
            else:
                new_tasks.append(task)
        return completed, new_tasks

    def _update_tqdm_progress_bar(self, pbar: tqdm) -> None:
        """Updates tqdm progress bar"""

        total_completed = 0
        for file_path in self._tqdm_tracking_dir.iterdir():
            total_completed += int(file_path.read_text())
        pbar.update(total_completed - pbar.n)

    ############################
    # Data Aggregation Methods #
    ############################

    def _run_chunk(self, chunk_id: int, trials: list[int]) -> GraphDataAggregator:
        """Runs a chunk of trial inputs"""

        # Must also seed randomness here since we don't want multiproc to be the same
        self._seed_random(seed_suffix=str(chunk_id))

        engine = self._get_engine_for_run_chunk()

        graph_data_aggregator = self.GraphDataAggregatorCls(
            graph_categories=self.graph_categories
        )

        for i, trial in self._get_run_chunk_iter(trials):
            # Use the same attacker victim pairs across all percent adoptions
            trial_attacker_asns = None
            trial_victim_asns = None
            for percent_adopt in self.percent_adoptions:
                # Use the same adopting asns across all scenarios configs
                adopting_asns = None
                for scenario_config in self.scenario_configs:
                    # Create the scenario for this trial
                    assert scenario_config.ScenarioCls, "ScenarioCls is None"
                    scenario = scenario_config.ScenarioCls(
                        scenario_config=scenario_config,
                        percent_adoption=percent_adopt,  # type: ignore
                        engine=engine,
                        preprocess_anns_func=scenario_config.preprocess_anns_func,
                        attacker_asns=trial_attacker_asns,
                        victim_asns=trial_victim_asns,
                        adopting_asns=adopting_asns,
                    )

                    # Change AS Classes, seed announcements before propagation
                    scenario.setup_engine(engine)
                    # For each round of propagation run the engine
                    for propagation_round in range(scenario_config.propagation_rounds):
                        self._single_engine_run(
                            engine=engine,
                            percent_adopt=percent_adopt,  # type: ignore
                            trial=trial,  # type: ignore
                            scenario=scenario,
                            propagation_round=propagation_round,
                            graph_data_aggregator=graph_data_aggregator,
                        )
                    trial_attacker_asns = scenario.attacker_asns
                    trial_victim_asns = scenario.victim_asns
                    adopting_asns = scenario.adopting_asns
            # Used to track progress with tqdm
            self._write_tqdm_progress(chunk_id, i)

        self._write_tqdm_progress(chunk_id, i)

        return graph_data_aggregator

    def _get_engine_for_run_chunk(self) -> BaseSimulationEngine:
        """Returns SimulationEngine for the _run_chunk method

        engine isn't picklable or dillable, as it has weakrefs, which
        will deserialize to dead refs
        """
        constructor_kwargs = dict(self.as_graph_constructor_kwargs)
        constructor_kwargs["tsv_path"] = None
        as_graph: ASGraph = self.ASGraphConstructorCls(**constructor_kwargs).run()
        engine = self.SimulationEngineCls(
            as_graph,
            cached_as_graph_tsv_path=self.as_graph_constructor_kwargs.get("tsv_path"),
        )
        return engine

    def _get_run_chunk_iter(self, trials: list[int]) -> Iterator[tuple[int, int]]:
        """Returns iterator for trials with or without progress bar

        If there's only 1 cpu, run the progress bar here, else we run it elsewhere
        """

        if self.parse_cpus == 1:
            return tqdm(  # type: ignore
                enumerate(trials),
                total=len(trials),
                desc=f"Simulating {self.output_dir.name}",
            )
        else:
            return enumerate(trials)  # type: ignore

    def _write_tqdm_progress(self, chunk_id: int, index: int) -> None:
        """Writes total number of percent adoption trial pairs to file"""

        # If self.parse_cpus == 1, then no multiprocessing is used
        if self.parse_cpus > 1:
            with (self._tqdm_tracking_dir / f"{chunk_id}.txt").open("w") as f:
                f.write(str(index + 1))

    def _single_engine_run(
        self,
        *,
        engine: BaseSimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        graph_data_aggregator: GraphDataAggregator,
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
            graph_data_aggregator,
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
        graph_data_aggregator: GraphDataAggregator,
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

        graph_data_aggregator.track_trial_metrics(
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
        else:
            # This prevents problems if kwargs is reused more than once
            # outside of this file, since we modify it
            kwargs = deepcopy(kwargs)
        # Set defaults for kwargs
        kwargs["pickle_path"] = kwargs.pop("pickle_path", self.pickle_path)
        kwargs["graph_dir"] = kwargs.pop("graph_dir", self.output_dir / "graphs")
        kwargs["graph_categories"] = kwargs.pop(
            "graph_categories", self.graph_categories
        )
        if GraphFactoryCls:
            GraphFactoryCls(**kwargs).generate_graphs()
            print(f"\nWrote graphs to {kwargs['graph_dir']}")

    @property
    def graph_output_dir(self) -> Path:
        return self.output_dir / "graphs"
