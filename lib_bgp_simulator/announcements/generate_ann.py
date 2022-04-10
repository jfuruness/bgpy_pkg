from .announcement import Announcement
from ..enums import Relationships


def generate_ann(AnnCls,
                 origin_asn: int,
                 prefix: str,
                 timestamp: int,
                 roa_valid_length: bool,
                 roa_origin: int,
                 communities=(),
                 recv_relationship=Relationships.ORIGIN,
                 # Since generate_ann only creates an announcement
                 # with defaults for the Announcement class,
                 # Users may call this func with additional defaults,
                 # Potentially for subclasses of the Ann class
                 **ann_subclass_defaults) -> Announcement:
    """Generates announcements with defaults

    We must use this because pypy3.9 doesn't support
    dataclasses with slots with defaults

    Note that for subclasses of Ann, you can still use this func
    you just pass in any subclass defaults via ann_subclass_defaults
    """

    kwargs = {"prefix": prefix,
              "timestamp": timestamp,
              "as_path": (origin_asn,),
              "seed_asn": origin_asn,
              "recv_relationship": recv_relationship,
              "roa_valid_length": roa_valid_length,
              "roa_origin": roa_origin,
              "withdraw": False,
              "traceback_end": False,
              "communities": communities}
    kwargs.update(ann_subclass_defaults)

    return AnnCls(**kwargs)
