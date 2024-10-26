from typing import TYPE_CHECKING

from .aspa import ASPA

if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ASRA(ASPA):
    """ASRA: Esentially ASPA and checking neighbors at every AS together

    Originally we had this policy coded for ASPAwN, an extension of ASPA that
    we had developed independently of ASRA in parallel. Upon publishing an ASPA
    evaluation paper, we received feedback from an ASPA RFC author and converted
    ASPAwN into ASRA

    That being said, ASRA is not yet finalized, and at the time of this writing the
    draft wasn't even published. This policy assumes ASRA3 records (not specifying
    the neighbor type) and also assumes the strict algorithm.

    I also don't know why the draft is made out to be so complicated. I'm leaving
    the algorithm we used for ASPAwN below, as it's vastly simpler than the ASRA
    algorithm listed in the RFC but has the same effect. I've contacted an ASRA
    author and asked them to simplify it. Once ASRA becomes finalized I'll change
    the code below.
    """

    name = "ASRA"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:  # type: ignore
        """Combines ASPA valid and checking neighbors at every AS"""

        as_path = ann.as_path
        as_dict = self.as_.as_graph.as_dict
        for i, asn in enumerate(as_path):
            # Get the AS object for the current AS in the AS Path
            asra_as_obj = as_dict[asn]
            # If the AS is an ASRA AS
            if isinstance(asra_as_obj.policy, ASRA):
                # Check that both of it's neighbors are in the valid next hops
                for neighbor_index in (i - 1, i + 1):
                    # Can't use try except IndexError here, since -1 is a valid index
                    if 0 <= neighbor_index < len(as_path):
                        neighbor_asn = as_path[neighbor_index]
                        if neighbor_asn not in asra_as_obj.neighbor_asns:
                            return False
        return super()._valid_ann(ann, from_rel)
