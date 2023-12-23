from typing import Any, Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.bgpc import CPPSimulationEngine as _CPPSimulationEngine

from bgpy.simulation_engines.base import SimulationEngine
from bgpy.simulation_engines.base import Policy
from bgpy.simulation_engines.py_simulation_engine.policies import BGPSimplePolicy

# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from .cpp_announcement import CPPAnnouncement
    from bgpy.simulation_frameworks.py_simulation_framework import Scenario


class CPPSimulationEngine(SimulationEngine):
    """Wrapper around the C++ SimulationEngine to make it compatible with BGPy"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._cpp_simulation_engine: _CPPSimulationEngine = _CPPSimulationEngine()

    def __eq__(self, other) -> bool:
        """Returns if two simulators contain the same BGPDAG's"""

        # TODO: Read in announcements and add to ASGraph's local RIBs
        # Since this is just for testing, it doesn't need to be fast
        raise NotImplementedError

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

        policies_used: set[type[Policy]] = set(non_default_asn_cls_dict.values())
        policies_used.add(BasePolicyCls)

        self._cpp_simulation_engine.setup(
            announcements,
            BasePolicyCls.name,
            {asn: PolicyCls.name for asn, PolicyCls in non_default_asn_cls_dict},
        )
        self.ready_to_run_round += 1

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
        # Increment the ready to run round
        self.ready_to_run_round += 1

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        raise NotImplementedError
        return dict(vars(self))

    @classmethod
    def __from_yaml_dict__(
        cls: type["CPPSimulationEngine"], dct: dict[str, Any], yaml_tag: Any
    ) -> "CPPSimulationEngine":
        """This optional method is called when you call yaml.load()"""

        raise NotImplementedError
        return cls(**dct)
