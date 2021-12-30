from .announcement import Announcement as Ann
from .generate_ann import generate_ann
from ..enums import Prefixes, Timestamps


def gen_attacker_subprefix_ann(AnnCls,
                               attacker_asn: int,
                               victim_asn: int,
                               **extra_kwargs) -> Ann:
    return generate_ann(AnnCls,
                        attacker_asn,
                        Prefixes.SUBPREFIX.value,
                        Timestamps.ATTACKER.value,
                        roa_valid_length=False,
                        roa_origin=victim_asn,
                        **extra_kwargs)
