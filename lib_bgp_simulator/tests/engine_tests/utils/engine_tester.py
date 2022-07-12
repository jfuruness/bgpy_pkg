from copy import deepcopy
from pathlib import Path
from typing import List

from PIL import Image

from .diagram import Diagram
from .simulator_codec import SimulatorCodec
from ....simulation_engine import SimulationEngine
from ....simulation_framework import Subgraph


class EngineTester:
    """Tests an engine run"""

    def __init__(self,
                 base_dir,
                 conf,
                 overwrite=False,
                 codec=SimulatorCodec()):
        self.conf = conf
        self.overwrite = overwrite
        self.codec = codec
        # Needed to aggregate all diagrams
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Creates directory for this specific test
        self.test_dir = self.base_dir / self.conf.name
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
        scenario = deepcopy(self.conf.scenario)
        # Get's an engine that has been set up
        engine = self._get_engine()
        # Run engine
        for propagation_round in range(self.conf.propagation_rounds):
            engine.run(propagation_round=propagation_round,
                       scenario=scenario)
            kwargs = {"engine": engine,
                      "scenario": scenario,
                      "propagation_round": propagation_round}
            # By default, this is a no op
            scenario.post_propagation_hook(**kwargs)

        # Get traceback results {AS: Outcome}
        outcomes = Subgraph()._get_engine_outcomes(engine, self.conf.scenario)
        # Convert this to just be {ASN: Outcome} (Not the AS object)
        outcomes = {as_obj.asn: result for as_obj, result in outcomes.items()}
        # Store engine and traceback YAML
        self._store_yaml(engine, outcomes)
        # Create diagrams before the test can fail
        self._generate_diagrams()
        # Compare the YAML's together
        self._compare_yaml()

    def _get_engine(self):
        """Creates and engine and sets it up for runs"""

        engine = SimulationEngine(
            BaseASCls=self.conf.scenario.BaseASCls,
            peer_links=self.conf.graph.peer_links,
            cp_links=self.conf.graph.customer_provider_links)

        prev_scenario = deepcopy(self.conf.scenario)
        prev_scenario.non_default_as_cls_dict =\
            self.conf.non_default_as_cls_dict
        self.conf.scenario.setup_engine(engine, 0, prev_scenario)
        return engine

    def _store_yaml(self, engine, outcomes):
        """Stores YAML for the engine and outcomes

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

    def _generate_diagrams(self):
        """Generates diagrams"""

        # Load engines
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        # Load outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)

        # Write guess graph
        Diagram().generate_as_graph(
            engine_guess,
            self.conf.scenario,
            outcomes_guess,
            f"({self.conf.name} Guess)\n{self.conf.desc}",
            path=self.test_dir / "guess.gv",
            view=False)
        # Write ground truth graph
        Diagram().generate_as_graph(
            engine_gt,
            self.conf.scenario,
            outcomes_gt,
            f"({self.conf.name} Ground Truth)\n{self.conf.desc}",
            path=self.test_dir / "ground_truth.gv",
            view=False)
        # Aggregate all tests
        self._aggregate_diagrams()

    def _aggregate_diagrams(self):
        """Aggregates all test diagrams for readability into a PDF"""

        # Because we have too many tests, we need to aggregate them for
        # readability
        # https://stackoverflow.com/a/47283224/8903959
        images = [Image.open(x) for x in self.image_paths]
        converted_images = list()
        for img in images:
            if img.mode == "RGBA":
                converted_images.append(img.convert("RGB"))
                img.close()
            else:
                converted_images.append(img)

        # Aggregate all images into a PDF
        converted_images[0].save(self.aggregated_diagrams_path,
                                 "PDF",
                                 resolution=100.0,
                                 save_all=True,
                                 append_images=converted_images[1:])
        for img in converted_images:
            img.close()

    def _compare_yaml(self):
        """Compares YAML for ground truth vs guess for engine and outcomes"""

        # Compare Engine
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        assert engine_guess == engine_gt
        # Compare outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)
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

    @property
    def outcomes_ground_truth_path(self) -> Path:
        """Returns the path to the outcomes ground truth YAML"""

        return self.test_dir / "outcomes_gt.yaml"

    @property
    def outcomes_guess_path(self) -> Path:
        """Returns the path to the outcomes guess YAML"""

        return self.test_dir / "outcomes_guess.yaml"

    @property
    def aggregated_diagrams_path(self) -> Path:
        """Returns the path to the aggregated diagrams PDF"""

        return self.base_dir / "aggregated_diagrams.pdf"

    @property
    def image_paths(self) -> List[Path]:
        """Returns paths as strings for all images"""

        return list(sorted(self.base_dir.glob("*/*png")))
