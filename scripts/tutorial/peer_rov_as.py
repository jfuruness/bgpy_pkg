from bgpy import Announcement as Ann
from bgpy import BGPSimpleAS
from bgpy import Relationships


class PeerROVAS(BGPSimpleAS):
    """An AS that deploys ROV"""

    name: str = "TutorialPeerROV"

    # mypy doesn't understand that this func is valid
    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:  # type: ignore
        """Returns announcement validity

        Returns false if invalid by roa and coming from a peer,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        # Invalid by ROA is not valid by ROV
        # Since this type of real world ROV only does peer filtering, only peers here
        if ann.invalid_by_roa and ann.recv_relationship == Relationships.PEERS:
            return False
        # Use standard BGP to determine if the announcement is valid
        else:
            # Mypy doesn't map superclasses properly
            return super(PeerROVAS, self)._valid_ann(  # type: ignore
                ann, *args, **kwargs
            )
