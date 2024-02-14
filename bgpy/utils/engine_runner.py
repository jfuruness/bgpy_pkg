from pathlib import Path

from .engine_run_config import EngineRunConfig
from .simulator_codec import SimulatorCodec

from bgpy.as_graphs.base import AS
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework import Scenario
from bgpy.simulation_framework import MetricTracker
from bgpy.enums import Plane, SpecialPercentAdoptions, Outcomes


class EngineRunner:
    """Executes a single engine run. Useful for tests and API"""

    def __init__(
        self,
        base_dir: Path,
        conf: EngineRunConfig,
        codec: SimulatorCodec = SimulatorCodec(),
    ) -> None:
        self.conf: EngineRunConfig = conf
        self.codec: SimulatorCodec = codec
        # Needed to aggregate all diagrams
        self.base_dir: Path = base_dir

        self.storage_dir: Path = self.base_dir / self.conf.name
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def run_engine(self):
        """Performs a single engine run

        Takes in a scenario (initialized with adopt ASN, atk and vic ASN,
        and a graph
        The scenario + graph are used to build and seed the engine
        After the engine is seeded, the engine is run
        Data is collected from the engine
        The engine and traceback are output to YAML
        """

        # Get's an engine that has been set up
        # MUST BE DONE IN THIS ORDER so that scenario init get's passed the engine
        engine = self._get_engine()
        scenario = self.conf.scenario_config.ScenarioCls(
            scenario_config=self.conf.scenario_config,
            engine=engine,
            preprocess_anns_func=self.conf.scenario_config.preprocess_anns_func,
        )
        scenario.setup_engine(engine)

        # Run engine
        for round_ in range(self.conf.scenario_config.propagation_rounds):  # type: ignore
            engine.run(propagation_round=round_, scenario=scenario)
            # By default, these are both no ops
            for func in (scenario.pre_aggregation_hook, scenario.post_propagation_hook):
                func(engine=engine, propagation_round=round_, trial=0, percent_adopt=0)

        # Get traceback results {AS: Outcome}
        analyzer = self.conf.ASGraphAnalyzerCls(
            engine=engine,
            scenario=scenario,
            # Later we don't even use control plane
            # so just turn it off here
            data_plane_tracking=True,
            control_plane_tracking=False,
        )
        outcomes: dict[int, dict[int, int]] = analyzer.analyze()
        data_plane_outcomes = outcomes[Plane.DATA.value]
        # This comment is no longer relevant, we just store the ASN
        # Convert this to just be {ASN: Outcome} (Not the AS object)
        outcomes_yaml = dict(data_plane_outcomes)
        metric_tracker = self._get_trial_metrics(
            engine=engine,
            percent_adopt=0,
            trial=0,
            scenario=scenario,
            propagation_round=self.conf.scenario_config.propagation_rounds - 1,
            outcomes=outcomes,
        )
        # Store engine and traceback YAML
        self._store_data(engine, outcomes_yaml, metric_tracker)
        # Create diagrams before the test can fail
        self._generate_diagrams(scenario, metric_tracker)

        return engine, outcomes_yaml, metric_tracker, scenario

    def _get_engine(self) -> BaseSimulationEngine:
        """Creates and engine and sets it up for runs"""

        as_graph = self.conf.ASGraphCls(
            as_graph_info=self.conf.as_graph_info,
            BasePolicyCls=self.conf.scenario_config.BasePolicyCls,
        )

        return self.conf.SimulationEngineCls(as_graph)

    def _get_trial_metrics(
        self,
        engine: BaseSimulationEngine,
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes: dict[int, dict[int, int]],
    ) -> MetricTracker:
        # Get stored metrics
        metric_tracker = self.conf.MetricTrackerCls()
        metric_tracker.track_trial_metrics(
            engine=engine,
            percent_adopt=0,
            trial=0,
            scenario=scenario,
            propagation_round=self.conf.scenario_config.propagation_rounds - 1,
            outcomes=outcomes,
        )
        assert isinstance(metric_tracker, MetricTracker)
        return metric_tracker

    def _store_data(
        self,
        engine: BaseSimulationEngine,
        outcomes: dict[int, int],
        metric_tracker: MetricTracker,
    ):
        """Stores YAML for the engine, outcomes, and CSV for metrics.

        If ground truth doesn't exist, create it
        """

        # Save engine
        self.codec.dump(engine, path=self.engine_guess_path)
        # Save outcomes
        self.codec.dump(outcomes, path=self.outcomes_guess_path)
        self._store_metrics(metric_tracker)

    def _store_metrics(self, metric_tracker: MetricTracker) -> None:
        metric_tracker.write_data(
            csv_path=self.metrics_guess_path_csv,
            pickle_path=self.metrics_guess_path_pickle,
        )

    def _generate_diagrams(
        self, scenario: Scenario, metric_tracker: MetricTracker
    ) -> tuple[
        BaseSimulationEngine,
        dict[int, Outcomes],
        tuple[tuple["AS", ...], ...],
    ]:
        """Generates diagrams"""

        # Load engines
        engine_guess = self.codec.load(self.engine_guess_path)
        # Load outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)

        static_order = bool(self.conf.as_graph_info.diagram_ranks)
        diagram_obj_ranks = self._get_diagram_obj_ranks(engine_guess)

        # Write guess graph
        self.conf.DiagramCls().generate_as_graph(
            engine_guess,
            scenario,  # type: ignore
            outcomes_guess,
            f"({self.conf.name})\n{self.conf.desc}",  # type: ignore
            metric_tracker,
            diagram_obj_ranks,
            static_order=static_order,
            path=self.storage_dir / "guess.gv",
            view=False,
        )

        return engine_guess, outcomes_guess, diagram_obj_ranks

    def _get_diagram_obj_ranks(
        self, engine_guess: BaseSimulationEngine
    ) -> tuple[tuple[AS, ...], ...]:
        """Returns diagram ranks as AS objects

        First from diagram_ranks if set in the config
        If not set in config, uses propagation ranks instead
        """

        # You can hardcode particular propagation ranks for diagrams
        if self.conf.as_graph_info.diagram_ranks:
            diagram_obj_ranks_mut = list()
            for rank in self.conf.as_graph_info.diagram_ranks:
                diagram_obj_ranks_mut.append(
                    [engine_guess.as_graph.as_dict[asn] for asn in rank]
                )

            # Assert that you weren't missing any ASNs
            hardcoded_rank_asns: list[int] = list()
            for rank in self.conf.as_graph_info.diagram_ranks:
                hardcoded_rank_asns.extend(rank)
            err = "Hardcoded rank ASNs do not match AS graph ASNs"
            assert set(list(engine_guess.as_graph.as_dict.keys())) == set(
                hardcoded_rank_asns
            ), err
        else:
            # Done this way to satisfy mypy
            diagram_obj_ranks_mut = [
                list(x) for x in engine_guess.as_graph.propagation_ranks
            ]

        return tuple([tuple(x) for x in diagram_obj_ranks_mut])

    #########
    # Paths #
    #########

    @property
    def engine_guess_path(self) -> Path:
        """Returns the path to the engine's guess YAML"""

        return self.storage_dir / "engine_guess.yaml"

    @property
    def outcomes_guess_path(self) -> Path:
        """Returns the path to the outcomes guess YAML"""

        return self.storage_dir / "outcomes_guess.yaml"

    @property
    def metrics_guess_path_csv(self) -> Path:
        """Returns the path to the metrics guess YAML"""

        return self.storage_dir / "metrics_guess.csv"

    @property
    def metrics_guess_path_pickle(self) -> Path:
        """Returns the path to the metrics guess YAML"""

        return self.storage_dir / "metrics_guess.pickle"
