from .announcement import Announcement as Ann
from .generate_ann import generate_ann
from ..enums import Prefixes, Timestamps, ROAValidity

def gen_victim_prefix_ann(AnnCls, origin_asn: int, **extra_kwargs) -> Ann:
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.PREFIX.value,
                        Timestamps.VICTIM.value,
                        ROAValidity.VALID,
                        **extra_kwargs)


def gen_attacker_prefix_ann(AnnCls, origin_asn: int, **extra_kwargs) -> Ann:
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.PREFIX.value,
                        Timestamps.ATTACKER.value,
                        ROAValidity.INVALID,
                        **extra_kwargs)
