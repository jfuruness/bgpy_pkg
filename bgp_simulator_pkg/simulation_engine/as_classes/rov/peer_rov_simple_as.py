from ..bgp import BGPSimpleAS

from ...announcement import Announcement as Ann
from ....enums import Relationships


class PeerROVSimpleAS(BGPSimpleAS):
    """An AS that deploys ROV"""

    name: str = "PeerROVSimple"

    # mypy doesn't understand that this func is valid
    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:  # type: ignore
        """Returns announcement validity

        Returns false if invalid by roa,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        # Invalid by ROA is not valid by ROV AND IS FROM A PEER
        if ann.invalid_by_roa and ann.recv_relationship == Relationships.PEERS:
            return False
        # Use standard BGP to determine if the announcement is valid
        else:
            # Mypy doesn't map superclasses properly
            return super(PeerROVSimpleAS,  # type: ignore
                         self)._valid_ann(ann, *args, **kwargs)
