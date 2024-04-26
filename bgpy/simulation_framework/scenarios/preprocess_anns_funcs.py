from collections import deque
from typing import Callable, Optional, TYPE_CHECKING
import warnings

from bgpy.simulation_engine import BGPFull, ASPA, Pathend, PathEnd

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_framework.scenario import Scenario
    from bgpy.simulation_engine import Announcement as Ann, BaseSimulationEngine
    from bgpy.simulation_engine import Policy


PREPROCESS_ANNS_FUNC_TYPE = Callable[
    [
        "Scenario",
        tuple["Ann", ...],
        Optional["BaseSimulationEngine"],
        Optional["Scenario"],
    ],
    tuple["Ann", ...],
]


def noop(
    self_scenario: "Scenario",
    unprocessed_anns: tuple["Ann", ...],
    engine: Optional["BaseSimulationEngine"],
    prev_scenario: Optional["Scenario"],
) -> tuple["Ann", ...]:
    """No op, the default preprocessing step"""

    return unprocessed_anns


def forged_origin_export_all_hijack(
    self_scenario: "Scenario",
    unprocessed_anns: tuple["Ann", ...],
    engine: Optional["BaseSimulationEngine"],
    prev_scenario: Optional["Scenario"],
) -> tuple["Ann", ...]:
    """Makes the attack use an origin hijack to be valid by ROA"""

    processed_anns = list()

    valid_ann = _get_valid_by_roa_ann(self_scenario.victim_asns, unprocessed_anns)

    for ann in unprocessed_anns:
        # If the announcement is from the attacker
        if ann.invalid_by_roa:
            # if ann.prefix != valid_ann.prefix:
            #     raise NotImplementedError("TODO: get the valid origin per prefix")
            # Make the AS path be just the victim
            processed_ann = ann.copy(
                {
                    "as_path": (ann.origin, valid_ann.origin),
                    # Ann.copy overwrites seed_asn and traceback by default
                    # so include these here to make sure that doesn't happen
                    "seed_asn": ann.seed_asn,
                    "traceback_end": ann.traceback_end,
                }
            )
            processed_anns.append(processed_ann)

        else:
            processed_anns.append(ann)

    return tuple(processed_anns)


def origin_hijack(*args, **kwargs):  # type: ignore
    warnings.warn(
        "origin_hijack is deprecated and will be removed in a future version."
        " Please use forged_origin_export_all_hijack instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return forged_origin_export_all_hijack(*args, **kwargs)  # type: ignore


def shortest_path_export_all_hijack(
    self_scenario: "Scenario",
    unprocessed_anns: tuple["Ann", ...],
    engine: Optional["BaseSimulationEngine"],
    prev_scenario: Optional["Scenario"],
) -> tuple["Ann", ...]:
    """Makes the attack use shortest path export all to bypass pathsec protections

    Specifically useful against bgp-isec, ASPA, and pathend
    """

    processed_anns: list["Ann"] = list()

    valid_ann = _get_valid_by_roa_ann(self_scenario.victim_asns, unprocessed_anns)
    for ann in unprocessed_anns:
        if not ann.invalid_by_roa:
            processed_anns.append(ann)
            continue
        elif any(
            issubclass(x, (Pathend, PathEnd))
            for x in self_scenario.non_default_asn_cls_dict.values()
        ):
            shortest_as_path = _find_shortest_secondary_provider_path(
                valid_ann.origin, engine
            )
        elif any(
            issubclass(x, ASPA) for x in self_scenario.non_default_asn_cls_dict.values()
        ):
            shortest_as_path = _find_shortest_non_adopting_path_general(
                valid_ann.origin, self_scenario, engine
            )
        else:
            return forged_origin_export_all_hijack(
                self_scenario, unprocessed_anns, engine, prev_scenario
            )

        if shortest_as_path:
            # This can happen if the attacker is the shortest path
            # See shortest_path_export_all_aspa_simple_provider test (27)
            if shortest_as_path[0] == ann.as_path[0] and len(shortest_as_path) > 1:
                shortest_as_path = shortest_as_path[1:]
            processed_anns.append(
                ann.copy(
                    {
                        "as_path": ann.as_path + shortest_as_path,
                        # Ann.copy overwrites seed_asn and traceback by default
                        # so include these here to make sure that doesn't happen
                        "seed_asn": ann.seed_asn,
                        "traceback_end": ann.traceback_end,
                    }
                )
            )

        else:
            processed_anns.append(ann)
    return tuple(processed_anns)


def neighbor_spoofing_hijack(
    self_scenario: "Scenario",
    unprocessed_anns: tuple["Ann", ...],
    engine: Optional["BaseSimulationEngine"],
    prev_scenario: Optional["Scenario"],
) -> tuple["Ann", ...]:
    """Makes the attack use origin spoofing to be valid by ROA"""

    unprocessed_anns = shortest_path_export_all_hijack(
        self_scenario, unprocessed_anns, engine, prev_scenario
    )
    processed_anns = list()

    for ann in unprocessed_anns:
        # If the announcement is from the attacker
        if any(x in ann.as_path for x in self_scenario.attacker_asns):
            neighbor_asn = ann.as_path[0]
            assert neighbor_asn in self_scenario.attacker_asns
            # Make the AS path be just the victim
            processed_ann = ann.copy(
                {
                    "as_path": tuple(ann.as_path[1:]),
                    "next_hop_asn": neighbor_asn,
                    # Ann.copy overwrites seed_asn and traceback by default
                    # so include these here to make sure that doesn't happen
                    "seed_asn": ann.seed_asn,
                    "traceback_end": ann.traceback_end,
                }
            )
            processed_anns.append(processed_ann)
        else:
            processed_anns.append(ann)

    policies = set(list(self_scenario.non_default_asn_cls_dict.values()))
    policies.add(self_scenario.scenario_config.AdoptPolicyCls)
    policies.add(self_scenario.scenario_config.BasePolicyCls)

    bgp_policy_derived_classes = [x for x in policies if issubclass(x, BGPFull)]

    msg = (
        f"{bgp_policy_derived_classes} are subclasses of BGPFull\n"
        "Origin spoofing isn't compatible with the way we've implemented "
        "the RIBsIn, which deviates from real life (where announcements are "
        "just stored using path attributes). So you can't use origin spoofing "
        "with policies derived from BGPFull, only BGP"
    )
    assert not bgp_policy_derived_classes, msg

    return tuple(processed_anns)


################
# Helper funcs #
################


def _get_valid_by_roa_ann(
    victim_asns: frozenset[int], unprocessed_anns: tuple["Ann", ...]
) -> "Ann":
    """Returns an announcement that's valid by ROA"""

    if len(victim_asns) != 1:
        raise NotImplementedError("TODO")

    [victim_asn] = victim_asns

    # Get ann and make sure it's roa is valid
    victim_ann = None
    for unprocessed_ann in unprocessed_anns:
        if victim_asn == unprocessed_ann.origin:
            victim_ann = unprocessed_ann
            break

    if not victim_ann:
        raise NotImplementedError("TODO")

    if not victim_ann.valid_by_roa:
        raise ValueError("What's the point if victim_asn isn't valid?")

    return victim_ann


def _find_shortest_secondary_provider_path(
    root_asn: int, engine: Optional["BaseSimulationEngine"]
) -> Optional[tuple[int, ...]]:
    """Finds the shortest secondary provider

    Used for attacking pathend, which only looks at the first provider
    """

    assert engine, "mypy"
    root_as_obj = engine.as_graph.as_dict[root_asn]
    for first_provider in root_as_obj.providers:
        # You only need legit origin and their provider, you don't need three
        # for secondary_provider in first_provider.providers:
        #     return (secondary_provider.asn, first_provider.asn, root_asn)
        return (first_provider.asn, root_asn)
    # Some ASes don't have providers, and are stubs that are peered
    for first_peer in root_as_obj.peers:
        return (first_peer.asn, root_asn)
    # Strange case but it could happen
    for first_customer in root_as_obj.customers:
        return (first_customer.asn, root_asn)
    return None


def _find_shortest_non_adopting_path_general(
    root_asn: int,
    self_scenario: "Scenario",
    engine: Optional["BaseSimulationEngine"],
) -> Optional[tuple[int, ...]]:
    """Finds the shortest non adopting path from the root asn

    Announcements from customers > peers > providers, since
    policies like ASPA and bgp-isec would reject announcements
    that are already going to customers, etc. So even if the path
    is longer, it's better to be accepted by going to a provider
    """

    AdoptPolicyCls = self_scenario.scenario_config.AdoptPolicyCls

    def get_policy(as_: "AS") -> type["Policy"]:
        return self_scenario.non_default_asn_cls_dict.get(  # type: ignore
            as_.asn, self_scenario.scenario_config.BasePolicyCls
        )

    assert engine, "mypy"
    root_as = engine.as_graph.as_dict[root_asn]

    # {ASN: as_path to get here}
    # NOTE: I used to have AS as the key, but weakref.Proxy isn't hashable
    # https://stackoverflow.com/a/68273386/8903959
    visited = dict()

    # First, use BFS on provider relationships
    queue: deque[tuple["AS", tuple[int, ...]]] = deque([(root_as, (root_as.asn,))])
    while queue:
        as_, as_path = queue.popleft()
        if as_.asn not in visited:
            if not issubclass(get_policy(as_), AdoptPolicyCls):
                return as_path
            visited[as_.asn] = as_path
            for provider_as in engine.as_graph.as_dict[as_.asn].providers:
                if provider_as.asn not in visited:
                    queue.append((provider_as, (provider_as.asn,) + as_path))

    # Then, go in order of provider relationships
    # This is a nice optimization, since the dictionary maintains order
    # and BFS increments in order of distance
    for visited_asn, as_path in visited.copy().items():
        visited_as = engine.as_graph.as_dict[visited_asn]
        for peer_as in visited_as.peers:
            if not issubclass(get_policy(peer_as), AdoptPolicyCls):
                return (peer_as.asn,) + as_path
            elif peer_as.asn not in visited:
                visited[peer_as.asn] = (peer_as.asn,) + as_path

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
    """
    if len(engine.as_graph) > 100:
        if self_scenario.percent_adoption >= 0.8:
            input_clique_ases = [x for x in engine.as_graph if x.input_clique]
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + str(len(input_clique_ases)))
            print([x.policy.name for x in input_clique_ases])
            print(self_scenario.attacker_asns)
            print(
                [
                    len(engine.as_graph.as_dict[asn].neighbors)
                    for asn in self_scenario.attacker_asns
                ]
            )
        # TODO: fix
        # NOTE: It's just that at 90% adoption, when attackers and victims are
        # on the edge, this code doesn't get run (which is why it's fine)
        raise NotImplementedError(
            "Theres a bug in shortest path export all when run with 99% adoption that "
            "eats up all the RAM. Not going to fix it for now - just run with 90%"
            " or less adoption percentages. If someone wants support for more, please "
            "email jfuruness@gmail.com or submit a github issue"
        )

    non_adopting_customers = set()  # USING ASNs due to weakref.Proxy not hashable
    visited_asns = list(visisted)
    for visited_asn in visisted_asns:
        as_path = visited[visisted_asn]
        visited_as = engine.as_graph.as_dict[visited_asn]
        queue = deque([(visited_as, as_path)])
        while queue:
            as_, as_path = queue.popleft()
            old_visited_path = visited.get(as_.asn)
            if not issubclass(get_policy(as_), AdoptPolicyCls):
                non_adopting_customers.add(as_.asn)
                # If the old path doesn't exist or is larger than the new one
                if old_visited_path is None or (len(old_visisted_path) > len(as_path)):
                    visited[as_.asn] = as_path
                # Don't continue down the path, since all customers will obvi
                # have longer chains than this one
            else:
                old_visited_path = visited.get(as_.asn)
                # If the old path doesn't exist or is larger than the new one
                if old_visited_path is None or (len(old_visisted_path) > len(as_path)):
                    visited[as_.asn] = as_path
                for customer_as in engine.as_graph.as_dict[as_.asn].customers:
                    queue.append((customer_as, (customer_as.asn,) + as_path))
    if non_adopting_customers:
        non_adopting_customer_distances = {
            asn: len(visited[asn]) for asn in non_adopting_customers
        }
        sorted_non_adopting_customers = sorted(
            non_adopting_customer_distances.items(), key=lambda x: x[1]
        )
        best_asn = sorted_non_adopting_customers[0][0]
        return visited[best_asn]
    else:
        return None
    """

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
            shortest_provider_path = None
            for provider_asn in as_obj.provider_asns:
                provider_path = visited.get(provider_asn)
                if provider_path is not None:
                    if shortest_provider_path is None:
                        shortest_provider_path = provider_path
                    elif len(provider_path) < len(shortest_provider_path):  # type: ignore
                        shortest_provider_path = provider_path
            # relevant to root ASN
            if shortest_provider_path:
                new_as_path = (as_obj.asn,) + shortest_provider_path
                old_as_path = visited.get(as_obj.asn)
                if not old_as_path or len(old_as_path) > len(new_as_path):
                    visited[as_obj.asn] = new_as_path
                if not issubclass(get_policy(as_obj), AdoptPolicyCls):
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
        return None
