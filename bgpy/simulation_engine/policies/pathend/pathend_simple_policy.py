from typing import TYPE_CHECKING


from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class PathendSimplePolicy(BGPSimplePolicy):
    """An Policy that deploys Pathend"""

    name: str = "PathendSimple"

    def _valid_ann(self, ann: "Ann", *args, **kwargs) -> bool:  # type: ignore
        """Returns announcement validity by checking pathend records"""

        origin_asn = ann.origin
        origin_as_obj = self.as_.as_graph.as_dict[origin_asn]
        # If the origin is deploying pathend and the path is longer than 1
        if (
            isinstance(origin_as_obj.policy, PathendSimplePolicy)
            and len(ann.as_path) > 1
        ):
            # If the provider is real, do the loop check
            for provider in origin_as_obj.providers:
                if provider.asn == ann.as_path[-2]:
                    return super()._valid_ann(ann, *args, **kwargs)
            # Provider is fake, return False
            return False
        else:
            return super()._valid_ann(ann, *args, **kwargs)
