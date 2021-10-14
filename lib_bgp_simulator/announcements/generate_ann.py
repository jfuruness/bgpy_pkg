from .announcement import Announcement

def generate_ann(AnnCls,
                 origin_asn,
                 prefix,
                 timestamp,
                 roa_validity,
                 **extra_kwargs):
    kwargs = {"prefix": prefix,
              "timestamp": timestamp,
              "as_path": (origin_asn,),
              "seed_asn": origin_asn,
              "roa_validity": roa_validity,
              "withdraw": False,
              "traceback_end": False}
    kwargs.update(extra_kwargs)

    return AnnCls(**kwargs)
