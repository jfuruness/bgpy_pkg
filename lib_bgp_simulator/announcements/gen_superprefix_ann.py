from .announcement import Announcement as Ann
from .generate_ann import generate_ann
from ..enums import Prefixes, Timestamps


def gen_attacker_superprefix_ann(AnnCls,
                                 attacker_asn: int,
                                 **extra_kwargs) -> Ann:
    return generate_ann(AnnCls,
                        attacker_asn,
                        Prefixes.SUPERPREFIX.value,
                        Timestamps.ATTACKER.value,
                        roa_valid_length=None,
                        roa_origin=None,
                        **extra_kwargs)
