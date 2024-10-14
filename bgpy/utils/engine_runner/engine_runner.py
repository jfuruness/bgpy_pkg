from pathlib import Path

from bgpy.as_graphs.base import AS
from bgpy.shared.enums import Outcomes, Plane, SpecialPercentAdoptions
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework import GraphDataAggregator, Scenario

from .engine_run_config import EngineRunConfig
from .simulator_codec import SimulatorCodec


class EngineRunner:
    """Executes a single engine run. Useful for tests and API"""

    def __init__(
        self,
        conf: EngineRunConfig,
        base_dir: Path = Path.home() / "Desktop" / "engine_runs",
        codec: SimulatorCodec | None = None,
        dpi: int | None = None,
    ) -> None:
        self.conf: EngineRunConfig = conf
        self.codec: SimulatorCodec = codec if codec else SimulatorCodec()
        # Needed to aggregate all diagrams
        self.base_dir: Path = base_dir

        self.storage_dir: Path = self.base_dir / self.conf.name
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.dpi: int | None = dpi

    def run_engine(
        self,
    ) -> tuple[BaseSimulationEngine, dict[int, int], GraphDataAggregator, Scenario]:
        """Performs a single engine run

        Takes in a scenario (initialized with adopt ASN, atk and vic ASN,
        and a graph
        The scenario + graph are used to build and seed the engine
        After the engine is seeded, the engine is run
        Data is collected from the engine
        The engine and traceback are output to YAML
        """

        # Get's an engine that has been set up
        engine, scenario = self._get_engine_and_scenario()

        # Run engine
        for round_ in range(self.conf.scenario_config.propagation_rounds):
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
        graph_data_aggregator = self._get_graph_data(
            engine=engine,
            percent_adopt=0,
            trial=0,
            scenario=scenario,
            propagation_round=self.conf.scenario_config.propagation_rounds - 1,
            outcomes=outcomes,
        )
        # Store engine and traceback YAML
        self._store_data(engine, outcomes_yaml, graph_data_aggregator)
        # Create diagrams before the test can fail
        self._generate_diagrams(scenario, graph_data_aggregator)

        return engine, outcomes_yaml, graph_data_aggregator, scenario

    def _get_engine_and_scenario(self) -> tuple[BaseSimulationEngine, Scenario]:
        """Useful for website"""

        # MUST BE DONE IN THIS ORDER so that scenario init get's passed the engine
        engine = self._get_engine()
        scenario = self._get_scenario(engine=engine)
        scenario.setup_engine(engine)
        return engine, scenario

    def _get_engine(self) -> BaseSimulationEngine:
        """Creates and engine and sets it up for runs"""

        as_graph = self.conf.ASGraphCls(
            as_graph_info=self.conf.as_graph_info,
            BasePolicyCls=self.conf.scenario_config.BasePolicyCls,
            store_provider_cone_size=self.conf.requires_provider_cones,
            store_provider_cone_asns=self.conf.requires_provider_cones,
        )

        return self.conf.SimulationEngineCls(as_graph)

    def _get_scenario(self, engine: BaseSimulationEngine) -> Scenario:
        return self.conf.scenario_config.ScenarioCls(
            scenario_config=self.conf.scenario_config,
            engine=engine,
        )

    def _get_graph_data(
        self,
        engine: BaseSimulationEngine,
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes: dict[int, dict[int, int]],
    ) -> GraphDataAggregator:
        # Get stored metrics
        graph_data_aggregator = self.conf.GraphDataAggregatorCls()
        graph_data_aggregator.aggregate_and_store_trial_data(
            engine=engine,
            percent_adopt=0,
            trial=0,
            scenario=scenario,
            propagation_round=self.conf.scenario_config.propagation_rounds - 1,
            outcomes=outcomes,
        )
        assert isinstance(graph_data_aggregator, GraphDataAggregator)
        return graph_data_aggregator

    def _store_data(
        self,
        engine: BaseSimulationEngine,
        outcomes: dict[int, int],
        graph_data_aggregator: GraphDataAggregator,
    ):
        """Stores YAML for the engine, outcomes, and CSV for metrics.

        If ground truth doesn't exist, create it
        """

        # Save engine
        self.codec.dump(engine, path=self.engine_guess_path)
        # Save outcomes
        self.codec.dump(outcomes, path=self.outcomes_guess_path)
        self._store_graph_data(graph_data_aggregator)

    def _store_graph_data(self, graph_data_aggregator: GraphDataAggregator) -> None:
        graph_data_aggregator.write_data(
            csv_path=self.graph_data_guess_path_csv,
            pickle_path=self.graph_data_guess_path_pickle,
        )

    def _generate_diagrams(
        self, scenario: Scenario, graph_data_aggregator: GraphDataAggregator
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
            scenario,
            outcomes_guess,
            f"({self.conf.name})\n{self.conf.desc}",
            graph_data_aggregator,
            diagram_obj_ranks,
            static_order=static_order,
            path=self.storage_dir / "guess.gv",
            view=False,
            dpi=self.dpi,
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
            assert set(engine_guess.as_graph.as_dict.keys()) == set(
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
    def graph_data_guess_path_csv(self) -> Path:
        """Returns the path to the metrics guess YAML"""

        return self.storage_dir / "graph_data_guess.csv"

    @property
    def graph_data_guess_path_pickle(self) -> Path:
        """Returns the path to the metrics guess YAML"""

        return self.storage_dir / "graph_data_guess.pickle"
