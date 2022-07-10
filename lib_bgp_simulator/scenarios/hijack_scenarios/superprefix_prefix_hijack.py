from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...enums import Prefixes
from ...enums import Relationships
from ...enums import Timestamps


class SuperprefixPrefixHijack(SingleAtkVicAdoptClsScenario):
    """Superprefix prefix attack

    This is an attack where the attacker
    announces a prefix hijack (invalid by roa origin)
    and also announces a superprefix of the prefix (ROA unknown)
    and the victim announces their own prefix
    """

    __slots__ = ()

    def _get_announcements(self):
        """Returns victim+attacker prefix ann, attacker superprefix ann

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(self.AnnCls(prefix=Prefixes.PREFIX.value,
                                    as_path=(victim_asn,),
                                    timestamp=Timestamps.VICTIM.value,
                                    seed_asn=victim_asn,
                                    roa_valid_length=True,
                                    roa_origin=victim_asn,
                                    recv_relationship=Relationships.ORIGIN)

        for attacker_asn in self.attacker_asns:
            anns.append(self.AnnCls(prefix=Prefixes.PREFIX.value,
                                    as_path=(attacker_asn,),
                                    timestamp=Timestamps.ATTACKER.value,
                                    seed_asn=attacker_asn,
                                    roa_valid_length=True,
                                    roa_origin=self.victim_asns[0],
                                    recv_relationship=Relationships.ORIGIN)
            anns.append(self.AnnCls(prefix=Prefixes.SUPERPREFIX.value,
                                    as_path=(attacker_asn,),
                                    timestamp=Timestamps.ATTACKER.value,
                                    seed_asn=attacker_asn,
                                    roa_valid_length=None,
                                    roa_origin=None,
                                    recv_relationship=Relationships.ORIGIN)

        err = "Fix the roa_origins of the announcements for multiple victims"
        assert len(self.victim_asns) == 0, err

        return tuple(anns)
