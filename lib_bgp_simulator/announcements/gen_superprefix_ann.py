from .announcement import Announcement as Ann
from .generate_ann import generate_ann
from ..enums import Prefixes, Timestamps, ROAValidity

def gen_victim_superprefix_ann(AnnCls,
                               origin_asn,
                               roa_validity: ROAValidity = None,
                               **extra_kwargs) -> Ann:
    assert roa_validity is not None
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.SUPERPREFIX.value,
                        Timestamps.VICTIM.value,
                        roa_validity,
                        **extra_kwargs)


def gen_attacker_superprefix_ann(AnnCls,
                                 origin_asn: int,
                                 **extra_kwargs) -> Ann:
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.SUPERPREFIX.value,
                        Timestamps.ATTACKER.value,
                        ROAValidity.UNKNOWN,
                        **extra_kwargs)
