from typing import Any, Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.enums import Relationships
from bgpy.simulation_engine import Policy

from .base_simulation_engine import BaseSimulationEngine

# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class SimulationEngine(BaseSimulationEngine):
    """Python simulation engine representation"""

    ###############
    # Setup funcs #
    ###############

    def setup(
        self,
        announcements: tuple["Ann", ...] = (),
        BasePolicyCls: type[Policy] = Policy,
        non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            frozendict()  # type: ignore
        ),
        prev_scenario: Optional["Scenario"] = None,
        attacker_asns: frozenset[int] = frozenset(),
        AttackerBasePolicyCls: Optional[type[Policy]] = None,
    ) -> frozenset[type[Policy]]:
        """Sets AS classes and seeds announcements"""

        policies_used: frozenset[type[Policy]] = self._set_as_classes(
            BasePolicyCls,
            non_default_asn_cls_dict,
            prev_scenario,
            attacker_asns,
            AttackerBasePolicyCls,
        )
        self._seed_announcements(announcements, prev_scenario)
        self.ready_to_run_round = 0
        return policies_used

    def _set_as_classes(
        self,
        BasePolicyCls: type[Policy],
        non_default_asn_cls_dict: frozendict[int, type[Policy]],
        prev_scenario: Optional["Scenario"] = None,
        attacker_asns: frozenset[int] = frozenset(),
        AttackerBasePolicyCls: Optional[type[Policy]] = None,
    ) -> frozenset[type[Policy]]:
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        policy_classes_used = set()
        # Done here to save as much time  as possible
        for as_obj in self.as_graph:
            # Delete the old policy and remove references so that RAM can be reclaimed
            del as_obj.policy.as_
            # set the AS class to be the proper type of AS
            Cls = non_default_asn_cls_dict.get(as_obj.asn, BasePolicyCls)
            if AttackerBasePolicyCls and as_obj.asn in attacker_asns:
                Cls = AttackerBasePolicyCls
            as_obj.policy = Cls(as_=as_obj)
            policy_classes_used.add(Cls)

        # NOTE: even though the code below is more efficient than the code
        # above, for some reason it just breaks without erroring
        # likely a bug in pypy's weak references
        # for some reason the attacker is just never seeded the announcements
        # AttackerBasePolicyCls takes precendence for attacker_asns
        # if AttackerBasePolicyCls is not None:
        #    policy_classes_used.add(AttackerBasePolicyCls)
        #    for asn in attacker_asns:
        #        # Delete the old policy and remove references for RAM
        #        del as_obj.policy.as_
        #        # set the AS class to be the proper type of AS
        #        as_obj.policy = AttackerBasePolicyCls(as_=as_obj)

        return frozenset(policy_classes_used)

    def _seed_announcements(
        self,
        announcements: tuple["Ann", ...] = (),
        prev_scenario: Optional["Scenario"] = None,
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
            obj_to_seed.policy.seed_ann(ann)

    #####################
    # Propagation funcs #
    #####################

    def run(self, propagation_round: int = 0, scenario: Optional["Scenario"] = None):
        """Propogates announcements and ensures proper setup"""

        # Ensure that the simulator is ready to run this round
        if self.ready_to_run_round != propagation_round:
            raise Exception(f"Engine not set up to run for {propagation_round} round")
        assert scenario, "This can't be empty"

        # import time
        # start = time.perf_counter()
        # Propogate anns
        self._propagate(propagation_round, scenario)
        # print(f"prop time {time.perf_counter() - start}")
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

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return dict(vars(self))

    @classmethod
    def __from_yaml_dict__(
        cls: type["SimulationEngine"], dct: dict[str, Any], yaml_tag: Any
    ) -> "SimulationEngine":
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)
