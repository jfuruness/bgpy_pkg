from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..defaults import ASNs
from ..defaults import ASTypes
from ..defaults import subprefix_hijack_anns
from ..defaults import HijackLocalRib
from ..run_example import run_example


from ...engine.bgp_as import BGPAS
from ...engine.bgp_policy import BGPPolicy
from ...engine.bgp_ribs_as import BGPRIBSAS
from ...engine.bgp_ribs_policy import BGPRIBSPolicy


def test_hidden_hijack_bgp(tmp_path):
    r"""Hidden hijack example with BGP
    Figure 1a in our ROV++ paper

        1
         \
         2 - 3
        /     \
       777     666
    """

    # Graph data
    peers = [PeerLink(2, 3)]
    customer_providers = [CPLink(provider_asn=1, customer_asn=2),
                          CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                          CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value)]
    # Number identifying the type of AS class
    as_policies = {asn: BGPPolicy for asn in
                   list(range(1, 4)) + [ASNs.VICTIM.value, ASNs.ATTACKER.value]}

    # Local RIB data
    local_ribs = {
        1: HijackLocalRib(prefix_as_path=(1, 2, ASNs.VICTIM.value)),
        2: HijackLocalRib(prefix_as_path=(2, ASNs.VICTIM.value),
                          subprefix_as_path=(2, 3, ASNs.ATTACKER.value)),
        3: HijackLocalRib(prefix_as_path=(3, 2, ASNs.VICTIM.value),
                          subprefix_as_path=(3, ASNs.ATTACKER.value)),

        ASNs.VICTIM.value: HijackLocalRib(prefix_as_path=(ASNs.VICTIM.value,),
            subprefix_as_path=(ASNs.VICTIM.value, 2, 3, ASNs.ATTACKER.value,)),

        ASNs.ATTACKER.value: HijackLocalRib(subprefix_as_path=(ASNs.ATTACKER.value,),
            prefix_as_path=(ASNs.ATTACKER.value, 3, 2, ASNs.VICTIM.value,)),
    }

    run_example(tmp_path,
                peers=peers,
                customer_providers=customer_providers,
                as_policies=as_policies,
                announcements=subprefix_hijack_anns,
                local_ribs=local_ribs,
                BaseASCls=BGPAS)

def test_hidden_hijack_bgp_ribs(tmp_path):
    r"""Hidden hijack example with BGP
    Figure 1a in our ROV++ paper

        1
         \
         2 - 3
        /     \
       777     666
    """

    # Graph data
    peers = [PeerLink(2, 3)]
    customer_providers = [CPLink(provider_asn=1, customer_asn=2),
                          CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                          CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value)]
    # Number identifying the type of AS class
    as_policies = {asn: BGPRIBSPolicy for asn in
                   list(range(1, 4)) + [ASNs.VICTIM.value, ASNs.ATTACKER.value]}

    # Local RIB data
    local_ribs = {
        1: HijackLocalRib(prefix_as_path=(1, 2, ASNs.VICTIM.value)),
        2: HijackLocalRib(prefix_as_path=(2, ASNs.VICTIM.value),
                          subprefix_as_path=(2, 3, ASNs.ATTACKER.value)),
        3: HijackLocalRib(prefix_as_path=(3, 2, ASNs.VICTIM.value),
                          subprefix_as_path=(3, ASNs.ATTACKER.value)),

        ASNs.VICTIM.value: HijackLocalRib(prefix_as_path=(ASNs.VICTIM.value,),
            subprefix_as_path=(ASNs.VICTIM.value, 2, 3, ASNs.ATTACKER.value,)),

        ASNs.ATTACKER.value: HijackLocalRib(subprefix_as_path=(ASNs.ATTACKER.value,),
            prefix_as_path=(ASNs.ATTACKER.value, 3, 2, ASNs.VICTIM.value,)),
    }

    run_example(tmp_path,
                peers=peers,
                customer_providers=customer_providers,
                as_policies=as_policies,
                announcements=subprefix_hijack_anns,
                local_ribs=local_ribs,
                BaseASCls=BGPRIBSAS)
