from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.simulation_framework.scenario import Scenario
    from bgpy.simulation_engine import Announcement as Ann, BaseSimulationEngine


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


def origin_hijack(
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
            if ann.prefix != valid_ann.prefix:
                raise NotImplementedError("TODO: get the valid origin per prefix")
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
    print(valid_ann)
    for ann in unprocessed_anns:
        # TODO
        # NOTE: must set pathend valid to be False
        pass
    return tuple(processed_anns)


def origin_spoofing_hijack(
    self_scenario: "Scenario",
    unprocessed_anns: tuple["Ann", ...],
    engine: Optional["BaseSimulationEngine"],
    prev_scenario: Optional["Scenario"],
) -> tuple["Ann", ...]:
    """Makes the attack use origin spoofing to be valid by ROA"""

    processed_anns = list()

    valid_ann = _get_valid_by_roa_ann(self_scenario.victim_asns, unprocessed_anns)

    for ann in unprocessed_anns:
        # If the announcement is from the attacker
        if ann.invalid_by_roa:
            if ann.prefix != valid_ann.prefix:
                raise NotImplementedError("TODO: get the valid origin per prefix")
            # Make the AS path be just the victim
            processed_ann = ann.copy(
                {
                    "as_path": (valid_ann.origin,),
                    "next_hop_asn": ann.origin,
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
