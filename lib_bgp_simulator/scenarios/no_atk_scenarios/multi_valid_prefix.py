from .valid_prefix import ValidPrefix
from ...enums import Prefixes
from ...enums import Relationships
from ...enums import Timestamps


class MultiValidPrefix(ValidPrefix):
    """A valid prefix engine input with multiple victims"""

    __slots__ = ("victim_asns")

    def __init__(self, *args, **kwargs):
        self.victim_asns = kwargs.pop("victim_asns")
        super().__init__(*args, **kwargs)

    def _get_announcements(self):
        """Returns several valid prefix announcements"""
        if self.victim_asns is None:
            return None
        vic_anns = []
        for victim_asn in self.victim_asns:
            vic_anns.append(self.AnnCls(prefix=Prefixes.PREFIX.value,
                                        as_path=(victim_asn,),
                                        timestamp=Timestamps.VICTIM.value,
                                        seed_asn=victim_asn,
                                        roa_valid_length=True,
                                        roa_origin=victim_asn,
                                        recv_relationship=Relationships.ORIGIN)
                            )
        return vic_anns
