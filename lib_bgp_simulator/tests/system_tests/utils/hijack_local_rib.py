from ....engine import LocalRIB
from ....announcements import Announcement
from ....enums import Prefixes, Timestamps, ASNs, ROAValidity


class HijackLocalRIB(LocalRIB):
    """Local Rib for Subprefix Hijack for easy test writing"""

    def __init__(self,
                 prefix_vic_as_path=None,
                 prefix_atk_as_path=None,
                 superprefix_as_path=None,
                 subprefix_as_path=None,
                 other_anns=[]):
        super(HijackLocalRIB, self).__init__()
        anns = []
        if prefix_vic_as_path:
            anns.append(Announcement(prefix=Prefixes.PREFIX.value,
                                     timestamp=Timestamps.VICTIM.value,
                                     as_path=prefix_vic_as_path,
                                     seed_asn=ASNs.VICTIM.value,
                                     roa_validity=ROAValidity.VALID))
        if prefix_atk_as_path:
            anns.append(Announcement(prefix=Prefixes.PREFIX.value,
                                     timestamp=Timestamps.ATTACKER.value,
                                     as_path=prefix_atk_as_path,
                                     seed_asn=ASNs.ATTACKER.value,
                                     roa_validity=ROAValidity.INVALID))
        if superprefix_as_path:
            anns.append(Announcement(prefix=Prefixes.SUPERPREFIX.value,
                                     timestamp=Timestamps.ATTACKER.value,
                                     as_path=superprefix_as_path,
                                     seed_asn=ASNs.ATTACKER.value,
                                     roa_validity=ROAValidity.UNKNOWN))
 
        if subprefix_as_path:
            anns.append(Announcement(prefix=Prefixes.SUBPREFIX.value,
                                     timestamp=Timestamps.ATTACKER.value,
                                     as_path=subprefix_as_path,
                                     seed_asn=ASNs.ATTACKER.value,
                                     roa_validity=ROAValidity.INVALID))
 
        for ann in anns + other_anns:
            self[ann.prefix] = ann
