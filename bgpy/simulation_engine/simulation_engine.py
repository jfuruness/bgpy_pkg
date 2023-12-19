from typing import Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.as_graphs import ASGraph, CAIDAASGraph  # noqa
from bgpy.enums import Relationships


# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement
    from bgpy.simulation_engine.policies import BGPSimplePolicy
    from bgpy.simulation_framework import Scenario


class SimulationEngine:
    """BGPDAG subclass that supports announcement propogation

    This class must be first setup with the _setup function
    This resets all the ASes to their base state, and changes
    the classes to be adopting specific defensive policies
    Then the run function can be called, and propagation occurs
    """

    def __init__(self, as_graph: ASGraph):
        """Saves read_to_run_rund attr and inits superclass"""

        self.as_graph = as_graph
        # This indicates whether or not the simulator has been set up for a run
        # We use a number instead of a bool so that we can indicate for
        # each round whether it is ready to run or not
        self.ready_to_run_round: int = -1

    def __eq__(self, other) -> bool:
        """Returns if two simulators contain the same BGPDAG's"""

        if isinstance(other, SimulationEngine):
            rv = self.as_graph.as_dict == other.as_graph.as_dict
            assert isinstance(rv, bool), "Make mypy happy"
            return rv
        else:
            return NotImplemented

    ###############
    # Setup funcs #
    ###############

    def setup(
        self,
        BasePolicyCls: type["BGPSimplePolicy"] = BGPSimplePolicy,
        non_default_asn_cls_dict: dict[int, type["BGPSimplePolicy"]] = frozendict(),
        prev_scenario: Optional["Scenario"] = None,
    ) -> frozenset["BGPSimplePolicy"]:
        """Sets AS classes and seeds announcements"""

        policies_used: frozenset["BGPSimplePolicy"] = self._set_as_classes(
            BasePolicyCls, non_default_asn_cls_dict, prev_scenario
        )
        self._seed_announcements(self.announcements, prev_scenario)
        self.ready_to_run_round = 0
        return policies_used

    def _set_as_classes(
        self,
        BasePolicyCls: type["BGPSimplePolicy"],
        non_default_asn_cls_dict: dict[int, type["BGPSimplePolicy"]],
        prev_scenario: Optional["Scenario"] = None,
    ) -> frozenset["BGPSimplePolicy"]:
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        policy_classes_used = set()
        # Done here to save as much time  as possible
        BasePolicyCls = self.scenario_config.BasePolicyCls
        for as_obj in self.as_graph:
            # Delete the old policy and remove references so that RAM can be reclaimed
            del as_obj.policy.as_
            # set the AS class to be the proper type of AS
            Cls = non_default_asn_cls_dict.get(as_obj.asn, BasePolicyCls)
            as_obj.policy = Cls(as_=as_obj)
            policy_classes_used.add(Cls)
        return frozenset(policy_classes_used)

    def _seed_announcements(
        self,
        announcements: tuple[Announcement, ...],
        prev_scenario: Optional["Scenario"],
    ) -> None:
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        for ann in announcements:
            assert ann.seed_asn is not None
            # Get the AS object to seed at
            # Must ignore type because it doesn't see assert above
            obj_to_seed = self.as_graph.as_dict[ann.seed_asn]  # type: ignore
            # Ensure we aren't replacing anything
            err = "Seeding conflict"
            assert obj_to_seed.policy._local_rib.get_ann(ann.prefix) is None, err
            # Seed by placing in the local rib
            obj_to_seed.policy._local_rib.add_ann(ann)

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
        self._propagate(propagation_round, scenario)
        # Increment the ready to run round
        self.ready_to_run_round += 1

    def _propagate(self, propagation_round: int, scenario: "Scenario"):
        """Propogates announcements

        to stick with Gao Rexford, we propagate to
        0. providers
        2. peers
        3. customers
        """

        self._propagate_to_providers(propagation_round, scenario)
        self._propagate_to_peers(propagation_round, scenario)
        self._propagate_to_customers(propagation_round, scenario)

    def _propagate_to_providers(self, propagation_round: int, scenario: "Scenario"):
        """Propogate to providers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        for i, rank in enumerate(self.as_graph.propagation_ranks):
            # Nothing to process at the start
            if i > 0:
                # Process first because maybe it recv from lower ranks
                for as_obj in rank:
                    as_obj.policy.process_incoming_anns(
                        from_rel=Relationships.CUSTOMERS,
                        propagation_round=propagation_round,
                        scenario=scenario,
                    )
            # Send to the higher ranks
            for as_obj in rank:
                as_obj.policy.propagate_to_providers()

    def _propagate_to_peers(
        self, propagation_round: int, scenario: Optional["Scenario"]
    ):
        """Propagate to peers"""

        # The reason you must separate this for loop here
        # is because propagation ranks do not take into account peering
        # It'd be impossible to take into account peering
        # since different customers peer to different ranks
        # So first do customer to provider propagation, then peer propagation
        for as_obj in self.as_graph:
            as_obj.policy.propagate_to_peers()
        for as_obj in self.as_graph:
            as_obj.policy.process_incoming_anns(
                from_rel=Relationships.PEERS,
                propagation_round=propagation_round,
                scenario=scenario,
            )

    def _propagate_to_customers(self, propagation_round: int, scenario: "Scenario"):
        """Propagate to customers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        # So here we start at the highest rank(input_clique) and propagate down
        for i, rank in enumerate(reversed(self.as_graph.propagation_ranks)):
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.policy.process_incoming_anns(
                        from_rel=Relationships.PROVIDERS,
                        propagation_round=propagation_round,
                        scenario=scenario,
                    )
            for as_obj in rank:
                as_obj.policy.propagate_to_customers()
