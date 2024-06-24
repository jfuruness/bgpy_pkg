from typing import Any, Optional, TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPiSec(BGP):
    """Represents BGPiSec

    We deviate slightly from bgpsec in this implementation, since
    the bgp-isec paper showed that security 3rd path preference might as well
    be security never, so we remove the path preference mechanism completely,
    which should also make this easier to deploy
    """

    name = "BGP-iSec"

    def _policy_propagate(  # type: ignore
        self, neighbor: "AS", ann: "Ann", *args, **kwargs
    ) -> bool:
        """Sets BGPSec fields when propagating

        If sending to bgpsec, set next_as and keep bgpsec_as_path
        otherwise clear out both fields
        """

        send_ann = ann.copy(
            {
                "bgpsec_next_asn": neighbor.asn,
                "bgpsec_as_path": ann.bgpsec_as_path
            }
        )
        self._process_outgoing_ann(neighbor, send_ann, *args, **kwargs)
        return True

    # Mypy doesn't understand the superclass
    def _copy_and_process(  # type: ignore
        self,
        ann: "Ann",
        recv_relationship: "Relationships",
        overwrite_default_kwargs: Optional[dict[Any, Any]] = None,
    ) -> "Ann":
        """Sets the bgpsec_as_path.

        prepends ASN if valid, otherwise clears
        """
        bgpsec_as_path = (self.as_.asn,) + ann.bgpsec_as_path

        if overwrite_default_kwargs is None:
            overwrite_default_kwargs = {}

        overwrite_default_kwargs["bgpsec_as_path"] = overwrite_default_kwargs.get(
            "bgpsec_as_path", bgpsec_as_path
        )

        return super()._copy_and_process(
            ann, recv_relationship, overwrite_default_kwargs
        )

    def _valid_ann(
        self: "BGP",
        ann: "Ann",
        recv_relationship: "Relationships",
    ) -> bool:
        """Determine if an announcement is valid or should be dropped"""

        # Need to do all bgpisec mechanisms here
        # protected OTC
        # provider cone ID
        # transitive signatures
        # maybe others that I'm missing...
        raise NotImplementedError
