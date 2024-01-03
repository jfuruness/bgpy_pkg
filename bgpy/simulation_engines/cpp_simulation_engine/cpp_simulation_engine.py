import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.bgpc import get_engine
from bgpy.bgpc import CPPSimulationEngine as _CPPSimulationEngine

import bgpy
from bgpy.enums import CPPRelationships
from bgpy.simulation_engines.base import SimulationEngine
from bgpy.simulation_engines.base import Policy
from bgpy.simulation_engines.py_simulation_engine.policies import BGPSimplePolicy

from .cpp_announcement import CPPAnnouncement

# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.simulation_frameworks.py_simulation_framework import Scenario


class CPPSimulationEngine(SimulationEngine):
    """Wrapper around the C++ SimulationEngine to make it compatible with BGPy"""

    def __init__(self, *args, create_cpp_engine=True, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # This can be turned off during testing to reduce debug output
        if create_cpp_engine:
            if self.cached_as_graph_tsv_path and self.cached_as_graph_tsv_path.exists():
                self._cpp_simulation_engine: _CPPSimulationEngine = get_engine(
                    str(self.cached_as_graph_tsv_path)
                )
            else:
                # TODO: fix circular imports
                with TemporaryDirectory() as tmp_dir:
                    tsv_path = Path(tmp_dir) / "caida.tsv"
                    bgpy.as_graphs.base.ASGraphConstructor.write_tsv(
                        self.as_graph, tsv_path
                    )

                    try:
                        self._cpp_simulation_engine = get_engine(str(tsv_path))
                    except ValueError as e:
                        msg = f"is customer_cones set to False? {e}"
                        print(msg)
                        raise

    def get_announcements(self):
        return self._cpp_simulation_engine.get_announcements()

    ###############
    # Setup funcs #
    ###############

    def setup(
        self,
        announcements: tuple["CPPAnnouncement", ...] = (),
        BasePolicyCls: type[Policy] = BGPSimplePolicy,
        non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            frozendict()  # type: ignore
        ),
        prev_scenario: Optional["Scenario"] = None,
    ) -> frozenset[type[Policy]]:
        """Sets AS classes and seeds announcements"""

        if not all(isinstance(x, CPPAnnouncement) for x in announcements):
            raise TypeError("Not using CPPAnnouncement with CPPSimulationEngine")
        if not all(
            isinstance(x.recv_relationship, CPPRelationships) for x in announcements
        ):
            raise TypeError(
                "Not using CPPRelationship in CPPAnnouncement with CPPSimulationEngine"
            )

        policies_used: set[type[Policy]] = set(non_default_asn_cls_dict.values())
        policies_used.add(BasePolicyCls)
        # import time
        # start = time.perf_counter()
        self._cpp_simulation_engine.setup(
            announcements,
            BasePolicyCls.name,
            {
                asn: PolicyCls.name
                for asn, PolicyCls in non_default_asn_cls_dict.items()
            },
        )
        # print(f"{time.perf_counter() - start}s for engine setup")

        self.ready_to_run_round = 0

        # Do this so that diagrams generate properly
        # TODO: do this properly with patching...
        if "PYTEST_CURRENT_TEST" in os.environ:
            for asn, as_obj in self.as_graph.as_dict.items():
                Cls = non_default_asn_cls_dict.get(asn, BasePolicyCls)
                as_obj.policy = Cls(as_=as_obj)

        return frozenset(policies_used)

    #####################
    # Propagation funcs #
    #####################

    def run(self, propagation_round: int = 0, scenario: Optional["Scenario"] = None):
        """Propogates announcements and ensures proper setup"""

        # Ensure that the simulator is ready to run this round
        if self.ready_to_run_round != propagation_round:
            raise Exception(f"Engine not set up to run for {propagation_round} round")
        assert scenario, "This can't be empty"
        # Propogate anns
        self._cpp_simulation_engine.run(propagation_round)
        # self._cpp_simulation_engine.dump_local_ribs_to_tsv("/home/anon/local_ribs.tsv")
        # Increment the ready to run round
        self.ready_to_run_round += 1

    ##############
    # Yaml funcs #
    ##############

    def dump_local_ribs_to_tsv(self, tsv_path: Path) -> None:
        """Dumps anns to TSV"""

        self._cpp_simulation_engine.dump_local_ribs_to_tsv(str(tsv_path))

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()

        NOTE: Since this is just used for testing, it's okay to be slow here
        so I'm just going to do this the slow way
        """

        # {asn: [anns_at_local_rib]}
        announcements = self._cpp_simulation_engine.get_announcements()
        for asn, as_obj in self.as_graph.as_dict.items():
            for announcement in announcements[asn]:
                as_obj.policy._local_rib.add_ann(announcement)
        return {
            "as_graph": self.as_graph,
            "ready_to_run_round": self.ready_to_run_round,
        }

    @classmethod
    def __from_yaml_dict__(
        cls: type["CPPSimulationEngine"], dct: dict[str, Any], yaml_tag: Any
    ) -> "CPPSimulationEngine":
        """This optional method is called when you call yaml.load()"""

        return cls(create_cpp_engine=False, **dct)
