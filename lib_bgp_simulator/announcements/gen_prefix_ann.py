from .generate_ann import generator_ann
from ..enums import Prefixes, Timestamps, ROAValidity

def gen_victim_prefix_ann(AnnCls, origin_asn, **extra_kwargs):
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.PREFIX.value,
                        Timestamps.VICTIM.value,
                        ROAValidity.VALID,
                        **extra_kwargs)


def gen_attacker_prefix_ann(AnnCls, origin_asn, **extra_kwargs):
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.PREFIX.value,
                        Timestamps.ATTACKER.value,
                        ROAValidity.INVALID,
                        **extra_kwargs)
