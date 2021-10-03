import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..utils import run_example, HijackLocalRib

from ....enums import ASNs, Prefixes, Timestamps, ROAValidity, Relationships
from ....simulator.attacks import SubprefixHijack
from ....engine import LocalRib
from ....engine.bgp_policy import BGPPolicy
from ....engine.bgp_ribs_policy import BGPRIBSPolicy
from ....announcement import Announcement

@pytest.mark.parametrize("BasePolicyCls", [BGPPolicy, BGPRIBSPolicy])
def test_hidden_hijack_bgp(BasePolicyCls):
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
    as_policies = {asn: BasePolicyCls for asn in
                   list(range(1, 4)) + [ASNs.VICTIM.value, ASNs.ATTACKER.value]}

    vic_kwargs = {"prefix": Prefixes.PREFIX.value,
                  "timestamp": Timestamps.VICTIM.value,
                  "seed_asn": None,
                  "roa_validity": ROAValidity.VALID}
    atk_kwargs = {"prefix": Prefixes.SUBPREFIX.value,
                  "timestamp": Timestamps.ATTACKER.value,
                  "seed_asn": None,
                  "roa_validity": ROAValidity.VALID}



    # Local RIB data
    local_ribs = {
        1: ({Prefixes.PREFIX.value: Announcement(as_path=(1, 2, ASNs.VICTIM.value),
                                                         recv_relationship=Relationships.CUSTOMERS,
                                                         **vic_kwargs)}),
        2: ({Prefixes.PREFIX.value: Announcement(as_path=(2, ASNs.VICTIM.value),
                                                         recv_relationship=Relationships.CUSTOMERS,
                                                         **vic_kwargs),
                     Prefixes.SUBPREFIX.value: Announcement(as_path=(2, 3, ASNs.ATTACKER.value),
                                                         recv_relationship=Relationships.PEERS,
                                                         **atk_kwargs)}),
        3: ({Prefixes.PREFIX.value: Announcement(as_path=(3, 2, ASNs.VICTIM.value),
                                                         recv_relationship=Relationships.PEERS,
                                                         **vic_kwargs),
                     Prefixes.SUBPREFIX.value: Announcement(as_path=(3, ASNs.ATTACKER.value),
                                                         recv_relationship=Relationships.CUSTOMERS,
                                                         **atk_kwargs)}),
        ASNs.VICTIM.value:
           ({Prefixes.PREFIX.value: Announcement(as_path=(ASNs.VICTIM.value,),
                                                         recv_relationship=Relationships.ORIGIN,
                                                         **vic_kwargs),
                     Prefixes.SUBPREFIX.value: Announcement(as_path=(ASNs.VICTIM.value,
                                                                    2,
                                                                    3,
                                                                    ASNs.ATTACKER.value),
                                                         recv_relationship=Relationships.PROVIDERS,
                                                         **atk_kwargs)}),
        ASNs.ATTACKER.value:
           ({Prefixes.PREFIX.value: Announcement(as_path=(ASNs.ATTACKER.value,3, 2, ASNs.VICTIM.value),
                                                         recv_relationship=Relationships.PROVIDERS,
                                                         **vic_kwargs),
                     Prefixes.SUBPREFIX.value: Announcement(as_path=(ASNs.ATTACKER.value,),
                                                         recv_relationship=Relationships.ORIGIN,
                                                         **atk_kwargs)}),
    }

    run_example(peers=peers,
                customer_providers=customer_providers,
                as_policies=as_policies,
                announcements=SubprefixHijack().announcements,
                local_ribs=local_ribs)
