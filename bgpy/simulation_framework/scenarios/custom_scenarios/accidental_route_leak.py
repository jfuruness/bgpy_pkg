from typing import TYPE_CHECKING

from bgpy.enums import Relationships, SpecialPercentAdoptions, Timestamps

from .valid_prefix import ValidPrefix
from ..scenario import Scenario


if TYPE_CHECKING:
    from bgpy.simulation_engine import BaseSimulationEngine
    from bgpy.simulation_engine import Announcement as Ann


class AccidentalRouteLeak(ValidPrefix):
    """An accidental route leak of a valid prefix"""

    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        """Causes an accidental route leak

        Changes the valid prefix to be received from a customer
        so that in the second propagation round, the AS will export to all
        relationships

        NOTE: the old way of doing this was to simply alter the attackers
        local RIB and then propagate again. However - this has some drawbacks
        Then the attacker must deploy BGPPolicy (that uses withdrawals) and
        the entire graph has to propagate again. BGPPolicy (and subclasses
        of it) are MUCH slower than BGPSimplePolicy due to all the extra
        computations for withdrawals, RIBsIn, RIBsOut, etc. Additionally,
        propagating a second round after the ASGraph is __already__ full
        is wayyy more expensive than propagating when the AS graph is empty.

        Instead, we now get the announcement that the attacker needs to leak
        after the first round of propagating the valid prefix.
        Then we clear the graph, seed those announcements, and propagate again
        This way, we avoid needing BGPPolicy (since the graph has been cleared,
        there is no need for withdrawals), and we avoid propagating a second
        time after the graph is alrady full.

        Since this simulator treats each propagation round as if it all happens
        at once, this is possible.

        Additionally, you could also do the optimization in the first propagation
        round to only propagate from ASes that can reach the attacker. But we'll
        forgo this for now for simplicity.
        """

        if propagation_round == 0:
            announcements: list["Ann"] = list(self.announcements)  # type: ignore
            for attacker_asn in self.attacker_asns:
                if not engine.as_graph.as_dict[attacker_asn].policy._local_rib:
                    print("Attacker did not recieve announcement, can't leak. ")
                for prefix, ann in engine.as_graph.as_dict[
                    attacker_asn
                ].policy._local_rib.items():
                    announcements.append(
                        ann.copy(
                            {
                                "recv_relationship": Relationships.CUSTOMERS,
                                "seed_asn": attacker_asn,
                                "traceback_end": True,
                                "timestamp": Timestamps.ATTACKER.value,
                            }
                        )
                    )
            self.announcements = tuple(announcements)
            self.setup_engine(engine)
            engine.ready_to_run_round = 1
        elif propagation_round > 1:
            raise NotImplementedError

    def _get_attacker_asns(self, *args, **kwargs):
        """Gets attacker ASNs, overriding the valid prefix which has no attackers

        There is a very rare case where the attacker can not perform the route leak
        due to a disconnection, which happens around .1% in the CAIDA topology.
        In theory - you could just look at the provider cone of the victim,
        and then the peers of that provider cone (and of the victim itself), and
        then the customer cones of all of those ASes to get the list of possible
        valid attackers. However, we consider the attacker being unable to attack
        in extremely rare cases a valid result, and thus do not change the random
        selection. Doing so would also be a lot slower for a very extreme edge case
        """
        return Scenario._get_attacker_asns(self, *args, **kwargs)
