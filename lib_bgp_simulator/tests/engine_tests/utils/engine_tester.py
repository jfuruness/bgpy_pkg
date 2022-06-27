from copy import deepcopy
from pathlib import Path

from .simulator_codec import SimulatorCodec
from ....engine import SimulationEngine
from ....subgraphs import Subgraph


class EngineTester:
    """Tests an engine run"""

    def __init__(self,
                 base_dir,
                 test_conf,
                 codec=SimulatorCodec()):
        self.test_conf = test_conf
        self.codec = codec
        # Needed to aggregate all diagrams
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Creates directory for this specific test
        self.test_dir = self.base_dir / self.test_conf.name
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

        # Get's an engine that has been set up
        engine = self._get_engine(test_conf.scenario,
                                  test_conf.graph,
                                  test_conf.non_default_as_cls_dict,
                                  test_conf.BaseASCls)
        # Run engine
        for propagation_round in range(test_conf.propagation_rounds):
            engine.run(propagation_round=propagation_round,
                       scenario=deepcopy(test_conf.scenario))
        # Get traceback results {AS: Outcome}
        outcomes = Subgraph()._get_engine_outcomes(engine, test_conf.scenario)
        # Convert this to just be {ASN: Outcome} (Not the AS object)
        outcomes = {as_obj.asn: result for as_obj, result in outcomes.items()}
        # Store engine and traceback YAML
        self._store_yaml(engine, outcomes)
        # Create diagrams before the test can fail
        self._generate_diagrams()
        # Compare the YAML's together
        self._compare_yaml()

    def _get_engine(self, scenario, graph, non_default_as_cls_dict, BaseASCls):
        """Creates and engine and sets it up for runs"""

        engine = SimulationEngine(
            BaseASCls=BaseASCls,
            peer_links=graph.peer_links,
            customer_provider_links=graph.customer_provider_links)
        prev_scenario = deepcopy(scenario)
        prev_scenario.non_default_as_cls_dict = non_default_as_cls_dict
        scenario.setup_engine(engine, 0, prev_scenario)
        return engine

    def _store_yaml(self, engine, outcomes):
        """Stores YAML for the engine and outcomes

        If ground truth doesn't exist, create it
        """

        # Save engine
        self.codec.dump(engine, path=self.engine_guess_path)
        # Save engine as ground truth if ground truth doesn't exist
        if not self.engine_ground_truth_path.exists():
            self.codec.dump(engine, path=self.engine_gt_path)
        # Save outcomes
        self.codec.dump(outcomes, path=self.outcomes_guess_path)
        # Save outcomes as ground truth if ground truth doesn't exist
        if not self.outcomes_ground_truth_path.exists():
            self.codec.dump(outcomes, path=self.outcomes_gt_path)

    def _generate_diagrams(self):
        """Generates diagrams"""

        # TODO
        # First write the diagrams to the test_dir
        # Then recreate the aggregation in the base_dir
        pass

    def _compare_yaml(self):
        """Compares YAML for ground truth vs guess for engine and outcomes"""

        # Compare Engine
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_gt_path)
        assert engine_guess == engine_gt
        # Compare outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_gt_path)
        assert outcomes_guess == outcomes_gt

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

    def outcomes_ground_truth_path(self) -> Path:
        """Returns the path to the outcomes ground truth YAML"""

        return self.test_dir / "outcomes_gt.yaml"

    @property
    def outcomes_guess_path(self) -> Path:
        """Returns the path to the outcomes guess YAML"""

        return self.test_dir / "outcomes_guess.yaml"
