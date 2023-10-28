import csv
from pathlib import Path
import pickle
from pprint import pformat

from .diagram import Diagram
from .engine_test_config import EngineTestConfig
from .simulator_codec import SimulatorCodec
from bgpy.simulation_engine import SimulationEngine
from bgpy.simulation_framework import Scenario
from bgpy.simulation_framework import MetricTracker
from bgpy.enums import Plane, SpecialPercentAdoptions


class EngineTester:
    """Tests an engine run"""

    def __init__(
        self,
        base_dir: Path,
        conf: EngineTestConfig,
        overwrite: bool = False,
        codec: SimulatorCodec = SimulatorCodec(),
        DiagramCls: type[Diagram] = Diagram,
        SimulationEngineCls: type[SimulationEngine] = SimulationEngine,
        compare_metrics: bool = False,
    ):
        """Regarding the compare_metrics kwarg:

        There was quite a debate on whether or not the engine tester
        should compare metrics. There are a lot of cons for comparing
        metrics here. Every single time the metrics change, all of the
        test data needs to be overwritten. This means even if you add
        a new metric, the test data needs to be overwritten, even if it
        is unrelated to the metrics, and you'll need to double check the
        ground truth of everything once again. metrics are also very
        finnicky, if JSON or CSV layouts change, they are prone to breakage
        without actually being a true failure. If the layout changes then
        those files change in git, even though no code has been modified.
        On top of that, different
        simulation_frameworks for different projects have different
        metrick trackers, some of which are quite different, some of which
        have no metrics at all. It also breaks
        the single responsibility of these being engine tests, to test the
        engine, not the simulation_framework. metric tracker could also be
        tested with unit tests.

        As for the cons, some tests would require a full round of propagation
        for a true metric tracker test. While the majority of the feedback
        was to remove it, one project was already using it. In light of that,
        being able to compare metrics in this test class will remain a feature,
        but by default it will be off. I've left an example to show how
        other projects could implement their own versions of it.
        """

        self.conf = conf
        self.overwrite = overwrite
        self.codec = codec
        # Needed to aggregate all diagrams
        self.base_dir: Path = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Creates directory for this specific test
        self.test_dir: Path = self.base_dir / self.conf.name  # type: ignore
        self.test_dir.mkdir(exist_ok=True)

        self.DiagramCls: type[Diagram] = DiagramCls
        self.SimulationEngineCls: type[SimulationEngine] = SimulationEngineCls

        self.compare_metrics: bool = compare_metrics

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
        metric_tracker = self._get_trial_metrics(
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

        engine = self.SimulationEngineCls(
            BaseASCls=self.conf.scenario_config.BaseASCls,
            peer_links=self.conf.graph.peer_links,  # type: ignore
            cp_links=self.conf.graph.customer_provider_links,  # type: ignore
        )  # type: ignore

        scenario.setup_engine(engine, scenario)
        return engine

    def _get_trial_metrics(
        self,
        engine: SimulationEngine,
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes,
    ) -> MetricTracker:
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
        return metric_tracker

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

        if self.compare_metrics:
            self._store_metrics(metric_tracker)

    def _store_metrics(self, metric_tracker: MetricTracker) -> None:
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
        self.DiagramCls().generate_as_graph(
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
        self.DiagramCls().generate_as_graph(
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

        if self.compare_metrics:
            self._compare_metrics_to_gt()

    def _compare_metrics_to_gt(self):
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
        err = f"{pformat(metrics_guess[0])} {pformat(metrics_gt[0])}"
        guess_set = set([str(x) for x in metrics_guess])
        gt_set = set([str(x) for x in metrics_gt])
        assert guess_set == gt_set, err

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
