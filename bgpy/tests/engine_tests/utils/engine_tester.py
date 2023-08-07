import csv
from pathlib import Path
import pickle

from .diagram import Diagram
from .engine_test_config import EngineTestConfig
from .simulator_codec import SimulatorCodec
from bgpy.simulation_engine import SimulationEngine
from bgpy.enums import Plane


class EngineTester:
    """Tests an engine run"""

    def __init__(
        self,
        base_dir: Path,
        conf: EngineTestConfig,
        overwrite: bool = False,
        codec: SimulatorCodec = SimulatorCodec(),
    ):
        self.conf = conf
        self.overwrite = overwrite
        self.codec = codec
        # Needed to aggregate all diagrams
        self.base_dir: Path = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Creates directory for this specific test
        self.test_dir: Path = self.base_dir / self.conf.name  # type: ignore
        self.test_dir.mkdir(exist_ok=True)

    def test_engine(self):
        """Tests an engine run

        Takes in a scenario (initialized with adopt ASN, atk and vic ASN,
        and a graph
        The scenario + graph are used to build and seed the engine
        After the engine is seeded, the engine is run
        Data is collected from the engine
        The engine and traceback are output to YAML
        We then compare the current run's traceback and engine
            to the ground truth
        """

        # Get a fresh copy of the scenario
        scenario = self.conf.scenario_config.ScenarioCls(
            scenario_config=self.conf.scenario_config
        )
        # Get's an engine that has been set up
        engine = self._get_engine(scenario)
        # Run engine
        for round_ in range(self.conf.propagation_rounds):  # type: ignore
            engine.run(propagation_round=round_, scenario=scenario)
            # By default, these are both no ops
            for func in (scenario.pre_aggregation_hook, scenario.post_propagation_hook):
                func(engine=engine, propagation_round=round_, trial=0, percent_adopt=0)

        # Get traceback results {AS: Outcome}
        analyzer = self.conf.GraphAnalyzerCls(engine=engine, scenario=scenario)
        outcomes = analyzer.analyze()
        data_plane_outcomes = outcomes[Plane.DATA.value]
        # Convert this to just be {ASN: Outcome} (Not the AS object)
        outcomes_yaml = {
            as_obj.asn: result for as_obj, result in data_plane_outcomes.items()
        }
        # Get stored metrics
        metric_tracker = self.conf.MetricTrackerCls()
        metric_tracker.track_trial_metrics(
            engine=engine,
            percent_adopt=0,
            trial=0,
            scenario=scenario,
            propagation_round=self.conf.propagation_rounds - 1,
            outcomes=outcomes,
        )
        # Store engine and traceback YAML
        self._store_data(engine, outcomes_yaml, metric_tracker)
        # Create diagrams before the test can fail
        self._generate_diagrams(scenario, metric_tracker)
        # Compare the YAML's together
        self._compare_data()

    def _get_engine(self, scenario):
        """Creates and engine and sets it up for runs"""

        engine = SimulationEngine(
            BaseASCls=self.conf.scenario_config.BaseASCls,
            peer_links=self.conf.graph.peer_links,  # type: ignore
            cp_links=self.conf.graph.customer_provider_links,  # type: ignore
        )  # type: ignore

        scenario.setup_engine(engine, scenario)
        return engine

    def _store_data(self, engine, outcomes, metric_tracker):
        """Stores YAML for the engine, outcomes, and CSV for metrics.

        If ground truth doesn't exist, create it
        """

        # Save engine
        self.codec.dump(engine, path=self.engine_guess_path)
        # Save engine as ground truth if ground truth doesn't exist
        if not self.engine_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(engine, path=self.engine_ground_truth_path)
        # Save outcomes
        self.codec.dump(outcomes, path=self.outcomes_guess_path)
        # Save outcomes as ground truth if ground truth doesn't exist
        if not self.outcomes_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(outcomes, path=self.outcomes_ground_truth_path)

        metric_tracker.write_data(
            csv_path=self.metrics_guess_path_csv,
            pickle_path=self.metrics_guess_path_pickle,
        )
        # Save metrics as ground truth if ground truth doesn't exist
        if (
            not self.metrics_ground_truth_path_pickle.exists()
            or not self.metrics_ground_truth_path_csv.exists()
        ) or self.overwrite:
            metric_tracker.write_data(
                csv_path=self.metrics_ground_truth_path_csv,
                pickle_path=self.metrics_ground_truth_path_pickle,
            )

    def _generate_diagrams(self, scenario, metric_tracker):
        """Generates diagrams"""

        # Load engines
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        # Load outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)

        # You can hardcode particular propagation ranks for diagrams
        if self.conf.graph.diagram_ranks:
            diagram_ranks = list()
            for rank in self.conf.graph.diagram_ranks:
                diagram_ranks.append([engine_guess.as_dict[asn] for asn in rank])

            # Assert that you weren't missing any ASNs
            hardcoded_rank_asns = list()
            for rank in self.conf.graph.diagram_ranks:
                hardcoded_rank_asns.extend(rank)
            err = "Hardcoded rank ASNs do not match AS graph ASNs"
            assert set(list(engine_guess.as_dict.keys())) == set(
                hardcoded_rank_asns
            ), err
            static_order = True
        else:
            diagram_ranks = engine_guess.propagation_ranks
            static_order = False

        # Write guess graph
        Diagram().generate_as_graph(
            engine_guess,
            scenario,  # type: ignore
            outcomes_guess,
            f"({self.conf.name} Guess)\n{self.conf.desc}",  # type: ignore
            metric_tracker,
            diagram_ranks,
            static_order=static_order,
            path=self.test_dir / "guess.gv",
            view=False,
        )
        # Write ground truth graph
        Diagram().generate_as_graph(
            engine_gt,
            scenario,  # type: ignore
            outcomes_gt,
            f"({self.conf.name} Ground Truth)\n"  # type: ignore
            f"{self.conf.desc}",  # type: ignore
            metric_tracker,
            diagram_ranks,
            static_order=static_order,
            path=self.test_dir / "ground_truth.gv",
            view=False,
        )

    def _compare_data(self):
        """Compares YAML for ground truth vs guess for engine and outcomes"""

        # Compare Engine
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        assert engine_guess == engine_gt
        # Compare outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)
        assert outcomes_guess == outcomes_gt
        # Compare metrics CSV
        with self.metrics_guess_path_csv.open() as guess_f:
            with self.metrics_ground_truth_path_csv.open() as ground_truth_f:
                guess_lines = set([tuple(x) for x in csv.reader(guess_f)])
                gt_lines = set([tuple(x) for x in csv.reader(ground_truth_f)])
                assert gt_lines == guess_lines, self.metrics_guess_path_csv

        # Compare metrics YAML
        with self.metrics_guess_path_pickle.open("rb") as f:
            metrics_guess = pickle.load(f)
        with self.metrics_ground_truth_path_pickle.open("rb") as f:
            metrics_gt = pickle.load(f)
        assert metrics_guess == metrics_gt

    #########
    # Paths #
    #########

    @property
    def engine_ground_truth_path(self) -> Path:
        """Returns the path to the engine's ground truth YAML"""

        return self.test_dir / "engine_gt.yaml"

    @property
    def engine_guess_path(self) -> Path:
        """Returns the path to the engine's guess YAML"""

        return self.test_dir / "engine_guess.yaml"

    @property
    def outcomes_ground_truth_path(self) -> Path:
        """Returns the path to the outcomes ground truth YAML"""

        return self.test_dir / "outcomes_gt.yaml"

    @property
    def outcomes_guess_path(self) -> Path:
        """Returns the path to the outcomes guess YAML"""

        return self.test_dir / "outcomes_guess.yaml"

    @property
    def metrics_ground_truth_path_csv(self) -> Path:
        """Returns the path to the metrics ground truth YAML"""

        return self.test_dir / "metrics_gt.csv"

    @property
    def metrics_guess_path_csv(self) -> Path:
        """Returns the path to the metrics guess YAML"""

        return self.test_dir / "metrics_guess.csv"

    @property
    def metrics_ground_truth_path_pickle(self) -> Path:
        """Returns the path to the metrics ground truth YAML"""

        return self.test_dir / "metrics_gt.pickle"

    @property
    def metrics_guess_path_pickle(self) -> Path:
        """Returns the path to the metrics guess YAML"""

        return self.test_dir / "metrics_guess.pickle"
