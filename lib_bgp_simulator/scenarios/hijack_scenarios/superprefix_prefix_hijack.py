from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...announcements import generate_ann
from ...enums import Prefixes
from ...enums import Timestamps


class SuperprefixPrefixHijack(SingleAtkVicAdoptClsScenario):
    """Superprefix prefix attack

    This is an attack where the attacker
    announces a prefix hijack (invalid by roa origin)
    and also announces a superprefix of the prefix (ROA unknown)
    and the victim announces their own prefix
    """

    __slots__ = ()

    def _get_announcements(self, **ann_subclass_defaults):
        """Returns victim+attacker prefix ann, attacker superprefix ann

        generate_ann generates announcements with Announcement class defaults
        (for example, withdraw=False to indicate the announcement is not
        a withdrawal)
        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement, and pass in any additional
        defaults via ann_subclass_defaults
        """

        # Victim ann attrs
        vic_ann_attrs = {"AnnCls": self.AnnCls,
                         "origin_asn": self.victim_asn,
                         "prefix": Prefixes.PREFIX.value,
                         "timestamp": Timestamps.VICTIM.value,
                         "roa_valid_length": True,
                         "roa_origin": self.victim_asn}

        # Attacker ann attrs
        atk_prefix_ann_attrs = {"AnnCls": self.AnnCls,
                                "origin_asn": self.attacker_asn,
                                "prefix": Prefixes.PREFIX.value,
                                "timestamp": Timestamps.ATTACKER.value,
                                "roa_valid_length": True,
                                "roa_origin": self.victim_asn}

        # Attacker superprefix ann attrs
        atk_superprefix_ann_attrs = {"AnnCls": self.AnnCls,
                                     "origin_asn": self.attacker_asn,
                                     "prefix": Prefixes.SUPERPREFIX.value,
                                     "timestamp": Timestamps.ATTACKER.value,
                                     "roa_valid_length": None,
                                     "roa_origin": None}

        return (generate_ann(**vic_ann_attrs, **ann_subclass_defaults),
                generate_ann(**atk_prefix_ann_attrs, **ann_subclass_defaults),
                generate_ann(**atk_superprefix_ann_attrs,
                             **ann_subclass_defaults))
