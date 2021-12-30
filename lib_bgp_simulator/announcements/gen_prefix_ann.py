from .announcement import Announcement as Ann
from .generate_ann import generate_ann
from ..enums import Prefixes, Timestamps


def gen_victim_prefix_ann(AnnCls, origin_asn: int, **extra_kwargs) -> Ann:
    return generate_ann(AnnCls,
                        origin_asn,
                        Prefixes.PREFIX.value,
                        Timestamps.VICTIM.value,
                        roa_valid_length=True,
                        roa_origin=origin_asn,
                        **extra_kwargs)


def gen_attacker_prefix_ann(AnnCls,
                            attacker_asn: int,
                            victim_asn: int,
                            **extra_kwargs) -> Ann:
    kwargs = {"roa_valid_length": True, "roa_origin": victim_asn}
    kwargs.update(extra_kwargs)
    return generate_ann(AnnCls,
                        attacker_asn,
                        Prefixes.PREFIX.value,
                        Timestamps.ATTACKER.value,
                        **kwargs)
