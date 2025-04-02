from functools import lru_cache
from ipaddress import ip_network
from typing import TYPE_CHECKING

from bgpy.as_graphs import AS
from bgpy.shared.enums import Outcomes, Plane
from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine import BaseSimulationEngine

from .as_graph_analyzer import ASGraphAnalyzer

if TYPE_CHECKING:
    from bgpy.simulation_framework.scenarios import Scenario


class TracerouteAnalyzer(ASGraphAnalyzer):
    """Does a traceroute on a given prefix from every AS

    The difference between this and the ASGraphAnalyzer is that
    this is for a specific IP address. As far as development differences,
    the AS graph analyzer also precomputes, for every single AS, the
    most specific announcement and stores this in a dict. I don't see
    how that can be faster than doing so on the fly, so that's what I do
    now
    """

    def __init__(
        self,
        engine: BaseSimulationEngine,
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
        traceroute_ip_address: str = "",
    ) -> None:
        self.engine: BaseSimulationEngine = engine
        self.scenario: Scenario = scenario
        if not traceroute_ip_address:
            raise ValueError("Must pass in IP address")
        else:
            self.traceroute_ip_address = traceroute_ip_address
        self._data_plane_outcomes: dict[int, int] = dict()
        self._control_plane_outcomes: dict[int, int] = dict()
        self.outcomes: dict[int, dict[int, int]] = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }
        self.data_plane_tracking: bool = data_plane_tracking
        self.control_plane_tracking: bool = control_plane_tracking

    def _get_most_specific_ann(self, as_obj: AS) -> "Ann | None":
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        most_specific_ann = None
        for prefix, ann in as_obj.policy.local_rib.items():
            # If prefix is more specific and overlaps with the ip address
            if self._new_prefix_is_more_specific_and_overlapping(
                old_prefix_str=most_specific_ann.prefix,
                new_prefix_str=prefix,
                traceroute_ip_address_str=self.traceroute_ip_address,
            ):
                most_specific_ann = ann
        return most_specific_ann

    @lru_cache(max_size=1000)
    def _new_prefix_is_more_specific_and_overlapping(
        self,
        old_prefix_str: str | None,
        new_prefix_str: str,
        traceroute_ip_address_str: str,
    ) -> bool:
        """Checks if new prefix is more specific than old, and overlaps with ip_addr"""

        new_prefix = ip_network(new_prefix_str)
        traceroute_ip_address = ip_network(traceroute_ip_address_str)

        # New prefix covers the IP address
        if traceroute_ip_address.subnet_of(new_prefix):
            # If there is no prefix then the new prefix is best
            if old_prefix_str is None:
                return True
            # Check if new is more specific than old
            else:
                old_prefix = ip_network(old_prefix_str)
                err = f"Local RIB has duplicate prefixes {old_prefix}"
                assert old_prefix != new_prefix, err
                return old_prefix.subnet_of(new_prefix)
        else:
            return False

    def _get_as_outcome_data_plane(
        self, as_obj: AS, visited_asns: set[int] | None = None
    ) -> int:
        """Recursively returns the as outcome"""

        if as_obj.asn in self._data_plane_outcomes:
            return self._data_plane_outcomes[as_obj.asn]
        else:
            most_specific_ann = self._get_most_specific_ann(as_obj)
            outcome_int = self._determine_as_outcome_data_plane(
                as_obj, most_specific_ann, visited_asns
            )
            # We haven't traced back all the way on the AS path
            if outcome_int == Outcomes.UNDETERMINED.value:
                assert most_specific_ann, "If not disconnected, ann must exist"
                # next as in the AS path to traceback to
                # Ignore type because only way for this to be here
                # Is if the most specific "Ann" was NOT None.
                next_as = self.engine.as_graph.as_dict[
                    # NOTE: Starting in v4, this is the next hop,
                    # not the next ASN in the AS PATH
                    # This is more in line with real BGP and allows for more
                    # advanced types of hijacks such as origin spoofing hijacks
                    most_specific_ann.next_hop_asn
                ]
                visited_asns = visited_asns if visited_asns is not None else set()
                visited_asns.add(as_obj.asn)
                outcome_int = self._get_as_outcome_data_plane(next_as, visited_asns)
            assert outcome_int != Outcomes.UNDETERMINED.value, "Shouldn't be possible"

            self._data_plane_outcomes[as_obj.asn] = outcome_int
            return outcome_int
