from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from bgpy.caida_collector import BGPDAG, AS
from bgpy.enums import Relationships
from bgpy.simulation_engine.as_classes import BGPSimpleAS


# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.simulation_framework import Scenario


class SimulationEngine(BGPDAG):
    """BGPDAG subclass that supports announcement propogation

    This class must be first setup with the _setup function
    This resets all the ASes to their base state, and changes
    the classes to be adopting specific defensive policies
    Then the run function can be called, and propagation occurs
    """

    def __init__(
        self,
        *args,
        # Default AS class in the BGPDAG
        BaseASCls: type[AS] = BGPSimpleAS,
        **kwargs,
    ):
        """Saves read_to_run_rund attr and inits superclass"""

        super(SimulationEngine, self).__init__(
            *args, BaseASCls=BaseASCls, **kwargs
        )  # type: ignore
        # This indicates whether or not the simulator has been set up for a run
        # We use a number instead of a bool so that we can indicate for
        # each round whether it is ready to run or not
        self.ready_to_run_round: int = -1

    def __eq__(self, other) -> bool:
        """Returns if two simulators contain the same BGPDAG's"""

        if isinstance(other, SimulationEngine):
            rv = self.as_dict == other.as_dict
            assert isinstance(rv, bool), "Make mypy happy"
            return rv
        else:
            return NotImplemented

    def run(self, propagation_round: int = 0, scenario: Optional["Scenario"] = None):
        """Propogates announcements and ensures proper setup"""

        # Ensure that the simulator is ready to run this round
        if self.ready_to_run_round != propagation_round:
            raise Exception(f"Engine not set up to run for {propagation_round} round")
        # Propogate anns
        self._propagate(propagation_round, scenario)
        # Increment the ready to run round
        self.ready_to_run_round += 1

    def _propagate(
        self, propagation_round: Optional[int], scenario: Optional["Scenario"]
    ):
        """Propogates announcements

        to stick with Gao Rexford, we propagate to
        0. providers
        2. peers
        3. customers
        """

        self._propagate_to_providers(propagation_round, scenario)
        self._propagate_to_peers(propagation_round, scenario)
        self._propagate_to_customers(propagation_round, scenario)

    def _propagate_to_providers(
        self, propagation_round: Optional[int], scenario: Optional["Scenario"]
    ):
        """Propogate to providers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        for i, rank in enumerate(self.propagation_ranks):
            # Nothing to process at the start
            if i > 0:
                # Process first because maybe it recv from lower ranks
                for as_obj in rank:
                    as_obj.process_incoming_anns(
                        from_rel=Relationships.CUSTOMERS,
                        propagation_round=propagation_round,
                        scenario=scenario,
                    )
            # Send to the higher ranks
            for as_obj in rank:
                as_obj.propagate_to_providers()

    def _propagate_to_peers(
        self, propagation_round: Optional[int], scenario: Optional["Scenario"]
    ):
        """Propagate to peers"""

        # The reason you must separate this for loop here
        # is because propagation ranks do not take into account peering
        # It'd be impossible to take into account peering
        # since different customers peer to different ranks
        # So first do customer to provider propagation, then peer propagation
        for as_obj in self:
            as_obj.propagate_to_peers()
        for as_obj in self:
            as_obj.process_incoming_anns(
                from_rel=Relationships.PEERS,
                propagation_round=propagation_round,
                scenario=scenario,
            )

    def _propagate_to_customers(
        self, propagation_round: Optional[int], scenario: Optional["Scenario"]
    ):
        """Propagate to customers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        # So here we start at the highest rank(input_clique) and propagate down
        for i, rank in enumerate(reversed(self.propagation_ranks)):
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.process_incoming_anns(
                        from_rel=Relationships.PROVIDERS,
                        propagation_round=propagation_round,
                        scenario=scenario,
                    )
            for as_obj in rank:
                as_obj.propagate_to_customers()
