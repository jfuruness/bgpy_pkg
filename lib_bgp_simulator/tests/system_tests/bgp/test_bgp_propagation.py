import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..utils import run_example, HijackLocalRib

from ....enums import ASNs, Relationships
from ....announcement import Announcement
from ....simulator.attacks import SubprefixHijack

from ....engine.bgp_as import BGPAS
from ....engine.bgp_policy import BGPPolicy
from ....engine.bgp_ribs_policy import BGPRIBSPolicy
from ....engine.local_rib import LocalRib

@pytest.mark.parametrize("BasePolicyCls", [BGPPolicy, BGPRIBSPolicy])
def test_propagate_bgp(BasePolicyCls):
    r"""
    Test propagating up without multihomed support in the following test graph.
    Horizontal lines are peer relationships, vertical lines are customer-provider. 
                                                                             
      1                                                                         
      |                                                                         
      2---3                                                                     
     /|    \                                                                    
    4 5--6  7                                                                   
                                                                                
    Starting propagation at 5, all ASes should see the announcement.
    """
    # Graph data
    peers = [PeerLink(2, 3), PeerLink(5, 6)]
    customer_providers = [CPLink(provider_asn=1, customer_asn=2),
                          CPLink(provider_asn=2, customer_asn=5),
                          CPLink(provider_asn=2, customer_asn=4),
                          CPLink(provider_asn=3, customer_asn=7)]
    # Number identifying the type of AS class
    as_policies = {asn: BasePolicyCls for asn in
                   list(range(1, 8))}

    # Announcements
    prefix = '137.99.0.0/16'
    announcements = [Announcement(prefix=prefix, as_path=(5,),timestamp=0, seed_asn=5)]

    # Local RIB data
    local_ribs = {
        1: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(1, 2, 5))}),
        2: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(2, 5))}),
        3: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(3, 2, 5))}),
        4: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(4, 2, 5))}),
        5: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(5,))}),
        6: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(6, 5))}),
        7: LocalRib({prefix: Announcement(prefix=prefix, timestamp=0, as_path=(7, 3, 2, 5))}),
    }

    run_example(peers=peers,
                customer_providers=customer_providers,
                as_policies=as_policies,
                announcements=announcements,
                local_ribs=local_ribs)
