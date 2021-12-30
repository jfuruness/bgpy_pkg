from .announcement import Announcement
from ..enums import Relationships


def generate_ann(AnnCls,
                 origin_asn: int,
                 prefix: str,
                 timestamp: int,
                 roa_valid_length: bool,
                 roa_origin: int,
                 **extra_kwargs) -> Announcement:
    kwargs = {"prefix": prefix,
              "timestamp": timestamp,
              "as_path": (origin_asn,),
              "seed_asn": origin_asn,
              "recv_relationship": Relationships.ORIGIN,
              "roa_valid_length": roa_valid_length,
              "roa_origin": roa_origin,
              "withdraw": False,
              "traceback_end": False,
              "communities": tuple()}
    kwargs.update(extra_kwargs)

    return AnnCls(**kwargs)
