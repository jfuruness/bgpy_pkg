from .announcement import Announcement
from ..enums import Relationships, ROAValidity

def generate_ann(AnnCls,
                 origin_asn: int,
                 prefix: str,
                 timestamp: int,
                 roa_validity: ROAValidity,
                 **extra_kwargs) -> Announcement:
    kwargs = {"prefix": prefix,
              "timestamp": timestamp,
              "as_path": (origin_asn,),
              "seed_asn": origin_asn,
              "roa_validity": roa_validity,
              "recv_relationship": Relationships.ORIGIN,
              "withdraw": False,
              "traceback_end": False,
              "communities": tuple()}
    kwargs.update(extra_kwargs)

    return AnnCls(**kwargs)
