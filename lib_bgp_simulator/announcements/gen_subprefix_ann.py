from .generate_ann import generate_ann
from ..enums import Prefixes, Timestamps, ROAValidity


def gen_victim_subprefix_ann(AnnCls, origin_asn, roa_validity=None, **extra_kwargs):
    assert roa_validity is not None
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.SUBPREFIX.value,
                        Timestamps.VICTIM.value,
                        roa_validity,
                        **extra_kwargs)


def gen_attacker_subprefix_ann(AnnCls, origin_asn, **extra_kwargs):
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.SUBPREFIX.value,
                        Timestamps.ATTACKER.value,
                        ROAValidity.INVALID,
                        **extra_kwargs)
