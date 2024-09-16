from ipaddress import IPv4Network, IPv6Network, ip_network
from typing import TYPE_CHECKING

from roa_checker import ROAChecker, ROAValidity

from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine import BaseSimulationEngine

"""ROA helper funcs. I would move more but that would break mypy"""

if TYPE_CHECKING:
    from .scenario import Scenario


def _add_roa_info_to_anns(
    self: "Scenario",
    *,
    announcements: tuple["Ann", ...] = (),
    engine: BaseSimulationEngine | None = None,
) -> tuple["Ann", ...]:
    """Adds ROA Info to Announcements"""

    if self.roas:
        roa_checker = self._get_roa_checker()
        processed_anns = list()
        for ann in announcements:
            prefix = ip_network(ann.prefix)

            roa_origin = self._get_roa_origin(roa_checker, prefix, ann.origin)

            roa_valid_length = self._get_roa_valid_length(
                roa_checker, prefix, ann.origin
            )

            processed_anns.append(
                ann.copy(
                    {
                        "roa_valid_length": roa_valid_length,
                        "roa_origin": roa_origin,
                    }
                )
            )
        return tuple(processed_anns)
    else:
        return announcements


def _get_roa_checker(self: "Scenario") -> ROAChecker:
    """Returns ROAChecker populated with self.roas"""

    roa_checker = ROAChecker()
    for roa in self.roas:
        roa_checker.insert(roa.prefix, roa)
    return roa_checker


def _get_roa_origin(
    self: "Scenario",
    roa_checker: ROAChecker,
    prefix: IPv4Network | IPv6Network,
    origin: int,
) -> int | None:
    """Returns ROA origin"""

    roas = roa_checker.get_relevant_roas(prefix)
    if len(roas) == 0:
        return None
    elif len(roas) == 1:
        [roa] = roas
        return int(roa.origin)
    else:
        raise NotImplementedError


def _get_roa_valid_length(
    self: "Scenario",
    roa_checker: ROAChecker,
    prefix: IPv4Network | IPv6Network,
    origin: int,
) -> bool | None:
    """Returns ROA validity"""

    outcome = roa_checker.get_roa_outcome(prefix, origin)
    if outcome.validity in (
        ROAValidity.INVALID_LENGTH,
        ROAValidity.INVALID_LENGTH_AND_ORIGIN,
    ):
        return False
    elif outcome.validity == ROAValidity.UNKNOWN:
        return None
    elif outcome.validity in (ROAValidity.VALID, ROAValidity.INVALID_ORIGIN):
        return True
    else:
        raise NotImplementedError(f"Should never reach this {outcome.validity}")
