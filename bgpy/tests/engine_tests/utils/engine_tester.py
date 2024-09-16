import csv
import pickle
from pathlib import Path

from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework import GraphDataAggregator, Scenario
from bgpy.utils import EngineRunner


class EngineTester(EngineRunner):
    """Tests an engine run"""

    def __init__(
        self,
        *args,
        overwrite: bool = False,
        compare_graph_data: bool = False,
        **kwargs,
    ) -> None:
        """Regarding the compare_graph_data kwarg:

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

        self.overwrite: bool = overwrite
        self.compare_graph_data: bool = compare_graph_data
        super().__init__(*args, **kwargs)

        # Don't store metrics if we don't use them
        if not self.compare_graph_data:

            def noop(*args, **kwargs):
                pass

            self._store_metrics = noop

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

        engine, outcomes_yaml, graph_data_aggregator, scenario = self.run_engine()
        # Store engine and traceback YAML
        self._store_gt_data(engine, outcomes_yaml, graph_data_aggregator)
        # Create diagrams before the test can fail
        self._generate_gt_diagrams(scenario, graph_data_aggregator)
        # Compare the YAML's together
        self._compare_data()

    def _store_gt_data(
        self,
        engine: BaseSimulationEngine,
        outcomes: dict[int, int],
        graph_data_aggregator: GraphDataAggregator,
    ) -> None:
        """Stores GROUND TRUTH YAML for the engine, outcomes, and CSV for metrics.

        If ground truth doesn't exist, create it
        """

        # Save engine as ground truth if ground truth doesn't exist
        if not self.engine_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(engine, path=self.engine_ground_truth_path)
        # Save outcomes as ground truth if ground truth doesn't exist
        if not self.outcomes_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(outcomes, path=self.outcomes_ground_truth_path)

        self._store_gt_metrics(graph_data_aggregator)

    def _store_gt_metrics(self, graph_data_aggregator: GraphDataAggregator) -> None:
        """Stores metric ground truth

        For some reason, even with sorting, these files store
        differently, and this the git diffs include these files
        even though we don't even track them anymore

        To combat this, we now compare metrics, and only overwrite
        if the metrics are actually different

        This function is unfortunately stupid complicated to accomplish this
        """

        # Save metrics as ground truth if ground truth doesn't exist
        if (
            not self.graph_data_ground_truth_path_pickle.exists()
            or not self.graph_data_ground_truth_path_csv.exists()
        ):
            graph_data_aggregator.write_data(
                csv_path=self.graph_data_ground_truth_path_csv,
                pickle_path=self.graph_data_ground_truth_path_pickle,
            )
        elif self.overwrite and self.graph_data_guess_path_pickle.exists():
            try:
                self._compare_graph_data_to_gt()
            # Metrics are actually different, write them out
            except AssertionError:
                graph_data_aggregator.write_data(
                    csv_path=self.graph_data_ground_truth_path_csv,
                    pickle_path=self.graph_data_ground_truth_path_pickle,
                )
        elif self.overwrite:
            try:
                # Write to guess first, so that we can compare
                graph_data_aggregator.write_data(
                    csv_path=self.graph_data_guess_path_csv,
                    pickle_path=self.graph_data_guess_path_pickle,
                )
                self._compare_graph_data_to_gt()
            # Metrics are actually different, write them out
            except AssertionError:
                graph_data_aggregator.write_data(
                    csv_path=self.graph_data_ground_truth_path_csv,
                    pickle_path=self.graph_data_ground_truth_path_pickle,
                )

    def _generate_gt_diagrams(
        self, scenario: Scenario, graph_data_aggregator: GraphDataAggregator
    ) -> None:
        """Generates diagrams for ground truth"""

        # Load engines
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        # Load outcomes
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)

        static_order = bool(self.conf.as_graph_info.diagram_ranks)
        diagram_obj_ranks = self._get_diagram_obj_ranks(engine_gt)

        # Write ground truth graph
        self.conf.DiagramCls().generate_as_graph(
            engine_gt,
            scenario,
            outcomes_gt,
            f"({self.conf.name} Ground Truth)\n" f"{self.conf.desc}",
            graph_data_aggregator,
            diagram_obj_ranks,
            static_order=static_order,
            path=self.storage_dir / "ground_truth.gv",
            view=False,
            dpi=self.dpi,
        )

    def _compare_data(self) -> None:
        """Compares YAML for ground truth vs guess for engine and outcomes"""

        # Compare Engine
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        assert engine_guess == engine_gt, f"{self.conf.name} failed engine check"
        # Compare outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)
        assert outcomes_guess == outcomes_gt, f"{self.conf.name} failed outcomes check"

        if self.compare_graph_data:
            self._compare_graph_data_to_gt()

    def _compare_graph_data_to_gt(self) -> None:
        # Compare metrics CSV
        with self.graph_data_guess_path_csv.open() as guess_f:
            with self.graph_data_ground_truth_path_csv.open() as ground_truth_f:
                guess_lines = {tuple(x) for x in csv.reader(guess_f)}
                gt_lines = {tuple(x) for x in csv.reader(ground_truth_f)}
                assert gt_lines == guess_lines, self.graph_data_guess_path_csv

        # Compare metrics YAML
        with self.graph_data_guess_path_pickle.open("rb") as f:
            graph_data_guess = pickle.load(f)  # noqa: S301
        with self.graph_data_ground_truth_path_pickle.open("rb") as f:
            graph_data_gt = pickle.load(f)  # noqa: S301

        for graph_category, data_point_dict in graph_data_guess.items():
            for data_point_key, agg_trial_data in data_point_dict.items():
                assert graph_data_gt[graph_category][data_point_key] == agg_trial_data
        for graph_category, data_point_dict in graph_data_gt.items():
            for data_point_key, agg_trial_data in data_point_dict.items():
                assert graph_data_guess[graph_category][data_point_key] == (
                    agg_trial_data
                )

    #########
    # Paths #
    #########

    @property
    def engine_ground_truth_path(self) -> Path:
        """Returns the path to the engine's ground truth YAML"""

        return self.storage_dir / "engine_gt.yaml"

    @property
    def outcomes_ground_truth_path(self) -> Path:
        """Returns the path to the outcomes ground truth YAML"""

        return self.storage_dir / "outcomes_gt.yaml"

    @property
    def graph_data_ground_truth_path_csv(self) -> Path:
        """Returns the path to the metrics ground truth YAML"""

        return self.storage_dir / "graph_data_gt.csv"

    @property
    def graph_data_ground_truth_path_pickle(self) -> Path:
        """Returns the path to the metrics ground truth YAML"""

        return self.storage_dir / "graph_data_gt.pickle"
