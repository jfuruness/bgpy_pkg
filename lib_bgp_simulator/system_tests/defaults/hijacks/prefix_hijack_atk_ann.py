from ..enums import ASNs, Prefixes, Timestamps
from ....announcement import Announcement
from ....roa_validity import ROAValidity


class PrefixHijackAtkAnn(Announcement):
    """Default subprefix hijack attacker announcement"""

    def __init__(self,
                 prefix=Prefixes.PREFIX.value,
                 timestamp=Timestamps.ATTACKER.value,
                 as_path=(ASNs.ATTACKER.value,),
                 seed_asn=ASNs.ATTACKER.value,
                 roa_validity=ROAValidity.INVALID):
        super(PrefixHijackAtkAnn, self).__init__(prefix=prefix,
                                                 timestamp=timestamp,
                                                 as_path=as_path,
                                                 roa_validity=roa_validity,
                                                 seed_asn=seed_asn)
