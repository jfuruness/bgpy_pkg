from typing import TYPE_CHECKING, Optional

from bgpy.as_graphs import AS
from bgpy.shared.enums import Outcomes

from .as_graph_analyzer import ASGraphAnalyzer

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class InterceptionASGraphAnalyzer(ASGraphAnalyzer):
    """Takes in a BaseSimulationEngine and outputs metrics

    For this specific ASGraphAnalyzer, the attacker ONLY succeeds
    if they are able to perform an interception attack and keep
    the original connection alive
    """

    def _get_as_outcome_data_plane(self, as_obj: AS) -> int:
        """Recursively returns the as outcome"""

        if as_obj.asn in self._data_plane_outcomes:
            return self._data_plane_outcomes[as_obj.asn]
        else:
            most_specific_ann = self._most_specific_ann_dict[as_obj]
            outcome_int = self._determine_as_outcome_data_plane(
                as_obj, most_specific_ann
            )
            # Continue tracing back. Only succeed if it goes back to the victim
            if outcome_int == Outcomes.ATTACKER_SUCCESS.value:
                assert most_specific_ann, "If outcome==attacker, ann must exist"
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

                # If next hop is this AS, return disconnected since we didn't
                # get back to the victim
                if next_as is as_obj:
                    self._data_plane_outcomes[as_obj.asn] = Outcomes.DISCONNECTED.value
                    return Outcomes.DISCONNECTED.value
                else:
                    next_as_outcome_int = self._get_as_outcome_data_plane(next_as)
                    # Next AS tunnels back to victim, return attacker success
                    if next_as_outcome_int in (
                        Outcomes.ATTACKER_SUCCESS.value,
                        Outcomes.VICTIM_SUCCESS.value,
                    ):
                        self._data_plane_outcomes[as_obj.asn] = outcome_int
                        return outcome_int
                    # Attacker fails and the route is disconnected
                    elif next_as_outcome_int == Outcomes.DISCONNECTED.value:
                        self._data_plane_outcomes[as_obj.asn] = next_as_outcome_int
                        return next_as_outcome_int
                    else:
                        raise NotImplementedError("Should never reach here")
            # We haven't traced back all the way on the AS path
            elif outcome_int == Outcomes.UNDETERMINED.value:
                assert most_specific_ann, "if outcome != disconnected, ann exists"
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
                outcome_int = self._get_as_outcome_data_plane(next_as)
                assert outcome_int != Outcomes.UNDETERMINED.value, "not possible"
                self._data_plane_outcomes[as_obj.asn] = outcome_int
                return outcome_int
            elif outcome_int == Outcomes.VICTIM_SUCCESS.value:
                self._data_plane_outcomes[as_obj.asn] = outcome_int
                return outcome_int
            else:
                raise NotImplementedError("Shouldn't be possible")

    def _determine_as_outcome_data_plane(
        self, as_obj: AS, most_specific_ann: Optional["Ann"]
    ) -> int:
        """Determines the outcome at an AS

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if as_obj.asn in self.scenario.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS.value
        elif as_obj.asn in self.scenario.victim_asns:
            return Outcomes.VICTIM_SUCCESS.value
        elif (
            most_specific_ann is None
            or len(most_specific_ann.as_path) == 1
            or most_specific_ann.next_hop_asn == as_obj.asn
        ):
            return Outcomes.DISCONNECTED.value
        else:
            return Outcomes.UNDETERMINED.value
