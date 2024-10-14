import warnings
from collections import deque
from typing import TYPE_CHECKING, Optional

from bgpy.shared.constants import bgpy_logger
from bgpy.shared.enums import (
    Prefixes,
    Relationships,
    SpecialPercentAdoptions,
    Timestamps,
)
from bgpy.simulation_engine import (
    ASPA,
    ASRA,
    BGP,
    ROV,
    ASPAFull,
    ASRAFull,
    BGPFull,
    BGPiSec,
    BGPiSecFull,
    BGPiSecTransitive,
    BGPiSecTransitiveFull,
    BGPiSecTransitiveOnlyToCustomers,
    BGPiSecTransitiveOnlyToCustomersFull,
    BGPiSecTransitiveProConID,
    BGPiSecTransitiveProConIDFull,
    BGPSec,
    BGPSecFull,
    EdgeFilter,
    EdgeFilterFull,
    EnforceFirstAS,
    EnforceFirstASFull,
    OnlyToCustomers,
    OnlyToCustomersFull,
    PathEnd,
    PathEndFull,
    PeerROV,
    PeerROVFull,
    Policy,
    ProviderConeID,
    ProviderConeIDFull,
    ROVEdgeFilter,
    ROVEdgeFilterFull,
    ROVEnforceFirstAS,
    ROVEnforceFirstASFull,
    ROVFull,
    ROVPPV1Lite,
    ROVPPV1LiteFull,
    ROVPPV2ImprovedLite,
    ROVPPV2ImprovedLiteFull,
    ROVPPV2Lite,
    ROVPPV2LiteFull,
    ShortestPathPrefixASPAAttacker,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.pre_rov import PrefixHijack
from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix,
)

from .forged_origin_prefix_hijack import ForgedOriginPrefixHijack

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class ShortestPathPrefixHijack(VictimsPrefix):
    """Shortest path allowed by defense set by AdoptPolicyCls against a prefix"""

    RequiredASPAAttackerCls = ShortestPathPrefixASPAAttacker

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix with path manipulation
        """

        # First get the victims prefix
        victim_anns = super()._get_announcements(engine=engine)
        attacker_anns = self._get_shortest_path_attacker_anns(engine=engine)
        return victim_anns + attacker_anns

    def _get_shortest_path_attacker_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns announcements for the shortest path attacker"""

        if self.scenario_config.AdoptPolicyCls in self.pre_rov_policy_classes:
            # Types are a bit messed due to mixins
            return self._get_prefix_attacker_anns(engine=engine)  # type: ignore
        elif self.scenario_config.AdoptPolicyCls in self.rov_policy_classes:
            # Types are a bit messed due to mixins
            return self._get_forged_origin_attacker_anns(engine=engine)  # type: ignore
        elif self.scenario_config.AdoptPolicyCls in self.pathend_policy_classes:
            return self._get_pathend_attack_anns(engine=engine)
        elif self.scenario_config.AdoptPolicyCls in self.aspa_policy_classes:
            return self._get_aspa_attack_anns(engine=engine)
        elif self.scenario_config.AdoptPolicyCls in self.asra_policy_classes:
            return self._get_aspa_attack_anns(
                engine=engine, require_aspa_attacker_cls=False
            )
        elif self.scenario_config.AdoptPolicyCls in self.bgpisec_policy_classes:
            # See post_propagation_hook - this is where the attack takes place
            # This must happen this way since bgpisec requires an actual ann
            # whereas ASPA just requires a "potential/plausible" ann
            return ()
        else:
            raise NotImplementedError(
                "Need to code shortest path attack against "
                f"{self.scenario_config.AdoptPolicyCls}"
            )

    # Using mixins instead of weird subclassing, SLF001 is wrong here (private vars)
    _get_prefix_attacker_anns = PrefixHijack._get_prefix_attacker_anns  # noqa: SLF001
    _get_forged_origin_attacker_anns = (
        # Using mixins instead of weird subclassing, SLF001 is wrong here (private vars)
        ForgedOriginPrefixHijack._get_forged_origin_attacker_anns  # noqa: SLF001
    )

    def _get_pathend_attack_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Get shortest path undetected by Path-End"""

        assert engine, "mypy"
        if len(self.victim_asns) > 1:
            raise NotImplementedError

        root_as_obj = engine.as_graph.as_dict[next(iter(self.victim_asns))]
        root_asn = root_as_obj.asn
        shortest_valid_path: tuple[int, ...] | None = None
        for first_provider in root_as_obj.providers:
            # You only need legit origin and their provider, you don't need three
            # for secondary_provider in first_provider.providers:
            #     return (secondary_provider.asn, first_provider.asn, root_asn)
            shortest_valid_path = (first_provider.asn, root_asn)
            break
        if not shortest_valid_path:
            # Some ASes don't have providers, and are stubs that are peered
            for first_peer in root_as_obj.peers:
                shortest_valid_path = (first_peer.asn, root_asn)
                break

        if not shortest_valid_path:
            # Strange case but it could happen
            for first_customer in root_as_obj.customers:
                shortest_valid_path = (first_customer.asn, root_asn)
                break

        if shortest_valid_path is None:
            warnings.warn(
                "Shortest path against pathend is none? "
                "This should only happen at full adoption...",
                stacklevel=2,
            )
            shortest_valid_path = ()

        assert shortest_valid_path is not None, "mypy"
        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn, *shortest_valid_path),
                    timestamp=Timestamps.ATTACKER.value,
                    next_hop_asn=attacker_asn,
                    seed_asn=attacker_asn,
                )
            )
        return tuple(anns)

    def _get_aspa_attack_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
        require_aspa_attacker_cls: bool = True,
    ) -> tuple["Ann", ...]:
        """Get shortest path undetected by ASPA"""

        if len(self.victim_asns) > 1:
            raise NotImplementedError

        if require_aspa_attacker_cls:
            self._validate_required_aspa_attacker_cls()

        assert engine, "mypy"

        shortest_valid_path = self._find_shortest_valley_free_non_adopting_path(
            root_asn=next(iter(self.victim_asns)), engine=engine
        )
        anns = list()
        for attacker_asn in self.attacker_asns:
            # There are cases where the attacker is a part of this
            # We add the attacker later so just remove it here
            current_shortest_valid_path = tuple(
                [x for x in shortest_valid_path if x != attacker_asn]
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn, *current_shortest_valid_path),
                    timestamp=Timestamps.ATTACKER.value,
                    next_hop_asn=attacker_asn,
                    seed_asn=attacker_asn,
                )
            )
        return tuple(anns)

    def _validate_required_aspa_attacker_cls(self) -> None:
        """Validates that AttackerBasePolicyCls is set correctly against ASPA"""

        if self.scenario_config.AttackerBasePolicyCls != self.RequiredASPAAttackerCls:
            raise ValueError(
                "For a shortest path export all attack against ASPA, "
                "scenario_config.AttackerAdoptPolicyCls must be set to "
                "ASPAShortestPathPrefixAttacker, which you can import like "
                "from bgpy.simulation_engine import ShortestPathPrefixASPAAttacker"
            )

    def _find_shortest_valley_free_non_adopting_path(
        self,
        root_asn: int,
        engine: "BaseSimulationEngine",
    ) -> tuple[int, ...]:
        """Finds the shortest non adopting path from the root asn

        Announcements from customers > peers > providers, since
        policies like ASPA and bgp-isec would reject announcements
        that are already going to customers, etc. So even if the path
        is longer, it's better to be accepted by going to a provider
        """

        AdoptPolicyCls = self.scenario_config.AdoptPolicyCls

        root_as = engine.as_graph.as_dict[root_asn]

        # {ASN: as_path to get here}
        # NOTE: I used to have AS as the key, but weakref.Proxy isn't hashable
        # https://stackoverflow.com/a/68273386/8903959
        visited = dict()

        # First, use BFS on provider relationships
        queue: deque[tuple[AS, tuple[int, ...]]] = deque([(root_as, (root_as.asn,))])
        while queue:
            as_, as_path = queue.popleft()
            if as_.asn not in visited:
                if not issubclass(self.get_policy_cls(as_), AdoptPolicyCls):
                    return as_path
                visited[as_.asn] = as_path
                for provider_as in engine.as_graph.as_dict[as_.asn].providers:
                    if provider_as.asn not in visited:
                        queue.append((provider_as, (provider_as.asn, *as_path)))

        # Then, go in order of provider relationships
        # This is a nice optimization, since the dictionary maintains order
        # and BFS increments in order of distance
        for visited_asn, as_path in visited.copy().items():
            visited_as = engine.as_graph.as_dict[visited_asn]
            for peer_as in visited_as.peers:
                if not issubclass(self.get_policy_cls(peer_as), AdoptPolicyCls):
                    return (peer_as.asn, *as_path)
                elif peer_as.asn not in visited:
                    visited[peer_as.asn] = (peer_as.asn, *as_path)

        # At this point, if we still haven't found it, it's a customer
        # relationship (or doesn't exist).
        # From here, the proper way to do things would be to use some modified
        # djikstras algorithm
        # But it's important to note that this is the uncommon case
        # since this would only occur if all of the input clique is adopting.
        # If that were the case, djikstras algorithm would have a very bad runtime
        # since 99% of ASes would be adopting
        # Additionally, this function only runs once per trial
        # for all these reasons, I'm not going to implement a modified djikstras,
        # which may be prone to error, and just do it the naive way, which is much
        # less error prone
        # To do this, I'll  simply iterate through all remaining ASes, and then sort
        # them and return the shortest AS path (or None)

        # BFS code removed here

        # The above commented out implementation basically did BFS using
        # customer relationships from every provider within the provider + peer
        # cone. The problem with that is you end up rechecking the same ASN
        # many different times, and you essentially are doing BFS 1000 times
        # due to the size of the provider + peer cone.
        # The only way to avoid rechecking the ASes, and avoid blowing up the RAM
        # is actually to use propagation ranks, since the graph is essentially ordered
        # As to why it seems to occur so frequently, when the input clique typically
        # should have non adopting ASNs, it's because about .2% of the CAIDA graph
        # gets disconnected. That means 99.8% of the time, a victim can reach the
        # input clique. But .998 ^ 1000 trials means ~13% chance that the victim
        # can reach the input clique every time. That's why we had to fix this,
        # even though in theory the problem should rarely occur.

        # So this is in the end doing something very similar to propagation
        # however, there are a few differences that I think make this worth keeping
        # 1. It's wayyyy faster than copying announcements and function call overhead
        #    especially with non-simple policies
        # 2. We can use this to modify any hijacks (whereas if this used propagation,
        #    it would be it's own scenario class
        # 3. The algo stops when it reaches a non adopting ASN, and the overwhelming
        #    majority of the time, that's going to be in the provider cone of the root
        #    asn, which is usually < 1000 ASes, which is going to be very fast
        # anyways, on with the propagation lol

        msg = "propagation ranks don't need reversal"
        assert engine.as_graph.propagation_ranks[-1][0].propagation_rank != 0, msg
        non_adopting_customer_asns = set()
        for propagation_rank in reversed(engine.as_graph.propagation_ranks):
            for as_obj in propagation_rank:
                shortest_provider_path: tuple[int, ...] | None = None
                for provider_asn in as_obj.provider_asns:
                    provider_path = visited.get(provider_asn)
                    if provider_path is not None and (
                        shortest_provider_path is None
                        or len(provider_path) < len(shortest_provider_path)
                    ):
                        shortest_provider_path = provider_path
                # relevant to root ASN
                if shortest_provider_path:
                    new_as_path = (as_obj.asn, *shortest_provider_path)
                    old_as_path = visited.get(as_obj.asn)
                    if not old_as_path or len(old_as_path) > len(new_as_path):
                        visited[as_obj.asn] = new_as_path
                    if not issubclass(self.get_policy_cls(as_obj), AdoptPolicyCls):
                        non_adopting_customer_asns.add(as_obj.asn)

        # Sort through non adopting customer ASNs to find shortest path
        if non_adopting_customer_asns:
            non_adopting_customer_paths = {
                asn: visited[asn] for asn in non_adopting_customer_asns
            }
            sorted_non_adopting_customer_paths = sorted(
                non_adopting_customer_paths.items(), key=lambda x: len(x[1])
            )
            best_asn, best_as_path = sorted_non_adopting_customer_paths[0]
            return best_as_path
        else:
            warnings.warn(
                "Shortest path against ASPA is none? "
                "This should only happen at full adoption...",
                stacklevel=2,
            )
            return ()

    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        """Performs Shortest path prefix hijack against BGPiSec classes

        For this attack, since bgp-isec transitive attributes are present,
        an actual announcement in a local RIB of an AS must be chosen
        (this assumes the attacker can see any local RIB through looking glass
        servers or route collectors, etc). This is unlike the theoretical shortest
        path like against ASPA (or in other words - when attacking ASPA you
        want the shortest plausible path. When attacking bgpisec you need the
        shortest path that exists).

        To do this, we iterate through all ASes and choose an announcement that
        has the shortest path in a local RIB where the last AS on the path is not
        adopting. Then the attacker appends their ASN and we repropagate.
        We could do this using algorithms and such depending on the class, but
        that can be a future improvement. For now I'm going for accuracy.

        A caveat for selecting the best shortest path - the attacker should always
        prefer announcements which have no OTC attributes over announcements with
        OTC attributes, since the attacker would then be detected less when
        propagating to providers.

        Additionally, much like an AccidentalRouteLeak, previously the attacker would
        simply modify their local RIB and then propagate again. However - this
        has some drawbacks. Then the attacker must deploy BGPFull
        (that uses withdrawals) and the entire graph has to propagate again.
        BGPFull (and subclasses of it) are MUCH slower than BGP due to all the extra
        computations for withdrawals, RIBsIn, RIBsOut, etc. Additionally,
        propagating a second round after the ASGraph is __already__ full
        is wayyy more expensive than propagating when the AS graph is empty.

        Instead, we now get the announcement that the attacker needs to leak
        after the first round of propagating the valid prefix.
        Then we clear the graph, seed those announcements, and propagate again
        This way, we avoid needing BGPFull (since the graph has been cleared,
        there is no need for withdrawals), and we avoid propagating a second
        time after the graph is alrady full.

        Since this simulator treats each propagation round as if it all happens
        at once, this is possible.
        """

        if self.scenario_config.AdoptPolicyCls not in self.bgpisec_policy_classes:
            return
        elif propagation_round == 0:
            # Force their to be two rounds of propagation
            # Can't set this in the class var since you only want it to apply here
            if self.scenario_config.propagation_rounds < 2:
                raise ValueError("Please set ScenarioConfig.propagation_rounds to 2")

            announcements: list[Ann] = list(self.announcements)

            # Find the best ann for attacker to fake with
            best_ann: Ann | None = None
            for _asn, as_obj in engine.as_graph.as_dict.items():
                # Search for an AS that doesn't next_hop signature
                if not isinstance(as_obj.policy, BGPiSecTransitive):
                    for ann in as_obj.policy.local_rib.values():
                        if best_ann is None:
                            best_ann = ann
                        # Prefer anns without OTC, always
                        elif ann.only_to_customers and not best_ann.only_to_customers:
                            continue
                        # Lastly prefer shorter paths
                        elif len(ann.as_path) < len(best_ann.as_path):
                            best_ann = ann
            if not best_ann:
                # NOTE: may be possible due to the 1% being all disconnected ASes
                # or when valid ann is in one of those disconnected ASes
                # this happens if you run 1k trials
                bgpy_logger.info(f"Couldn't find best_ann at {percent_adopt}% adoption")
                # When this occurs, use victim's ann to at least do forged-origin
                victim_as_obj = engine.as_graph.as_dict[next(iter(self.victim_asns))]
                for ann in victim_as_obj.policy.local_rib.values():
                    best_ann = ann

            assert best_ann, "mypy"
            # Add fake announcements
            assert self.attacker_asns, "You must select at least 1 AS to leak"
            for attacker_asn in self.attacker_asns:
                announcements.append(
                    best_ann.copy(
                        {
                            "as_path": (attacker_asn, *best_ann.as_path),
                            "recv_relationship": Relationships.ORIGIN,
                            "seed_asn": attacker_asn,
                            "timestamp": Timestamps.ATTACKER.value,
                            "next_hop_asn": attacker_asn,
                        }
                    )
                )

            # Reset the engine for the next run
            self.announcements = tuple(announcements)
            self.setup_engine(engine)
            engine.ready_to_run_round = 1
        elif propagation_round > 1:
            raise NotImplementedError

    ######################
    # Policy class lists #
    ######################

    @property
    def pre_rov_policy_classes(self) -> frozenset[type[Policy]]:
        """These are policy classes that are susceptible to pre_rov attacks

        such as prefix hijack, subprefix hijack
        """

        return frozenset(
            {
                BGP,
                BGPFull,
                OnlyToCustomers,
                OnlyToCustomersFull,
                EdgeFilter,
                EdgeFilterFull,
                EnforceFirstAS,
                EnforceFirstASFull,
            }
        )

    @property
    def rov_policy_classes(self) -> frozenset[type[Policy]]:
        """These are policy classes that are susceptible to forged-origin attacks"""

        return frozenset(
            {
                BGPSec,
                BGPSecFull,
                ROVEdgeFilter,
                ROVEdgeFilterFull,
                ROVEnforceFirstAS,
                ROVEnforceFirstASFull,
                ROV,
                ROVFull,
                PeerROV,
                PeerROVFull,
                ROVPPV1Lite,
                ROVPPV1LiteFull,
                ROVPPV2Lite,
                ROVPPV2LiteFull,
                ROVPPV2ImprovedLite,
                ROVPPV2ImprovedLiteFull,
                ProviderConeID,
                ProviderConeIDFull,
            }
        )

    @property
    def pathend_policy_classes(self) -> frozenset[type[Policy]]:
        """Policies susceptible to a Pathend Shortest Path attack

        i.e the third hop is where the attacker is placed
        """

        return frozenset({PathEnd, PathEndFull})

    @property
    def aspa_policy_classes(self) -> frozenset[type[Policy]]:
        """Policies susceptible to an ASPA Shortest Path attack

        i.e. shortest contiguous chain of ASPA providers ending in non adopter
        with forged-origin hijack sent to customers
        """

        return frozenset({ASPA, ASPAFull})

    @property
    def asra_policy_classes(self) -> frozenset[type[Policy]]:
        """Policies susceptible to an ASRA Shortest Path attack

        i.e. shortest contiguous chain of ASPA providers ending in non adopter
        """

        return frozenset({ASRA, ASRAFull})

    @property
    def bgpisec_policy_classes(self) -> frozenset[type[Policy]]:
        """Policies susceptible to an BGP-iSec Shortest Path attack

        i.e. shortest contiguous chain of BGP-iSec ASes ending in non adopter
        that uses actual announcements rather than plausible ones
        """

        return frozenset(
            {
                BGPiSecTransitive,
                BGPiSecTransitiveOnlyToCustomers,
                BGPiSecTransitiveProConID,
                BGPiSec,
                BGPiSecTransitiveFull,
                BGPiSecTransitiveOnlyToCustomersFull,
                BGPiSecTransitiveProConIDFull,
                BGPiSecFull,
            }
        )
