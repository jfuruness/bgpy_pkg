from copy import deepcopy
from pathlib import Path
from typing import Any, Union
import json
from shutil import make_archive
from tempfile import TemporaryDirectory
import time
from typing import Dict, Tuple
import warnings

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_framework import MetricTracker
from bgpy.simulation_framework import Scenario
from bgpy.simulation_engine import SimulationEngine
from bgpy.simulation_framework import Simulation

from .subgraphs import Subgraph


class SubgraphSimulation(Simulation):
    """Deprecated simulator that works off of subgraphs"""

    def __init__(
        self,
        *args,
        subgraphs: tuple[Subgraph, ...] = (),
        output_path: Path = Path("/tmp/graphs"),
        **kwargs,
    ) -> None:
        warnings.warn(
            "Deprecated, untested, please don't use. Leaving this until 2025"
            " so that a few PhD students can graduate :)",
            DeprecationWarning,
        )
        if subgraphs:
            self.subgraphs: Tuple[Subgraph, ...] = subgraphs
        else:
            self.subgraphs = tuple([Cls() for Cls in Subgraph.subclasses if Cls.name])

        self.output_path: Path = output_path
        # Overwrite this to return subgraphs
        # janky, but this is deprecated, no other way to do this
        kwargs["MetricTrackerCls"] = self._janky_subgraphs
        super().__init__(*args, **kwargs)

        # Not used in newest version, but in this version the graph_label is
        # used to store info. To change as a parameter, change the
        # scenario_label in the scenario_config
        scenarios = [x.ScenarioCls(scenario_config=x) for x in self.scenario_configs]
        labels = [x.graph_label for x in scenarios]
        assert len(labels) == len(set(labels)), "Scenario labels not unique"

    # Can't have as a lambda due to pickling issues
    def _janky_subgraphs(self):
        return deepcopy(getattr(self, "subgraphs"))

    def run(self, metadata=None, include_graphs=True):
        """Runs the simulation and write the data"""

        if metadata is None:
            metadata = dict()
        start = time.perf_counter()
        self._get_data()
        metadata["runtime_seconds"] = time.perf_counter() - start
        self._write_data(metadata, include_graphs)

    def _get_data(self):
        """Runs trials for graph and aggregates data"""

        # Single process
        if self.parse_cpus == 1:
            # Results are a list of lists of subgraphs
            results = self._get_single_process_results()
        # Multiprocess
        else:
            # Results are a list of lists of subgraphs
            results = self._get_mp_results(self.parse_cpus)

        # Results is a list of lists of subgraphs
        # This joins all results from all trials
        for result_subgraphs in results:
            # Janky type ignore, had to do it this way to get deprecated working
            zipped_vals = zip(self.subgraphs, result_subgraphs)  # type: ignore
            for self_subgraph, result_subgraph in zipped_vals:
                # Merges the trial subgraph into this subgraph
                self_subgraph.add_trial_info(result_subgraph)

    def _collect_engine_run_data(
        self,
        engine: SimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        metric_tracker: MetricTracker,
    ):
        """For each subgraph, aggregate data

        Some data aggregation is shared to speed up runs
        For example, traceback might be useful across
        Multiple subgraphs

        This is overriding another func to use this deprecated func
        """

        # Had to do it this way due to deprecation
        subgraphs: Tuple[Subgraph, ...] = metric_tracker  # type: ignore

        shared_data: Dict[Any, Any] = dict()
        for subgraph in subgraphs:
            subgraph.aggregate_engine_run_data(
                shared_data,
                engine=engine,
                # Done to remove the SpecialPercentAdoptions
                percent_adopt=float(percent_adopt),
                trial=trial,
                scenario=scenario,
                propagation_round=propagation_round,
            )

    def _write_data(self, metadata, include_graphs: bool):
        """Writes subgraphs in graph_dir"""

        # init JSON and temporary directory
        json_data = dict()
        with TemporaryDirectory() as tmp_dir:
            if include_graphs:
                # Write subgraph and add data to the JSON
                for subgraph in self.subgraphs:
                    subgraph.write_graphs(Path(tmp_dir))
                    json_data[subgraph.name] = subgraph.data
            # Save the JSON
            with (Path(tmp_dir) / "results.json").open("w") as f:
                json.dump(json_data, f, indent=4)

            # Save metadata
            with (Path(tmp_dir) / "metadata.json").open("w") as f:
                json.dump(metadata, f, indent=4)

            # Zip the data
            make_archive(self.output_path, "zip", tmp_dir)  # type: ignore
            print(f"\nWrote graphs to {self.output_path}.zip")
