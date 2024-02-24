from typing import TYPE_CHECKING


from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ROV(BGP):
    """An Policy that deploys ROV"""

    name: str = "ROV"

    # mypy doesn't understand that this func is valid
    def _valid_ann(self, ann: "Ann", *args, **kwargs) -> bool:  # type: ignore
        """Returns announcement validity

        Returns false if invalid by roa,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        # Invalid by ROA is not valid by ROV
        if ann.invalid_by_roa:
            return False
        # Use standard BGP to determine if the announcement is valid
        else:
            # Mypy doesn't map superclasses properly
            return super(ROV, self)._valid_ann(ann, *args, **kwargs)  # type: ignore
