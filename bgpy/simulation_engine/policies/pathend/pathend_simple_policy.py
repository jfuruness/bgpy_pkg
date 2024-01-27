from typing import TYPE_CHECKING


from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class PathendSimplePolicy(BGPSimplePolicy):
    """An Policy that deploys Pathend"""

    name: str = "PathendSimple"

    def _valid_ann(self, ann: "Ann", *args, **kwargs) -> bool:  # type: ignore
        """Returns announcement validity by checking pathend records"""

        raise NotImplementedError
        if ann.pathend_valid:
            return super(PathendSimplePolicy, self)._valid_ann(  # type: ignore
                *args,
                **kwargs
            )
        else:
            return False
