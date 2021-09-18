from copy import deepcopy

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships
from .run_example import run_example
from ..announcement import Announcement
from .hijack_local_rib import HijackLocalRib
from ..simulator.attacks import SubprefixHijack

from ..engine.bgp_as import BGPAS
from ..engine.bgp_policy import BGPPolicy
from ..engine.bgp_ribs_policy import BGPRIBSPolicy
from ..engine.local_rib import LocalRib

def test_process_incoming_anns_bgp():
    """Test basic functionality of process_incoming_anns"""
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # assert announcement was accepted to local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

def test_process_incoming_anns_bgp_duplicate():
    """Sanity check that duplicated announcements do not cause problems"""
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # assert announcement was accepted to local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

def test_process_incoming_anns_bgp_relationships():
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(13794,),timestamp=0)
    ann2 = Announcement(prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[13794][prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.recv_q[13795][prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    assert(a.policy.local_rib[prefix].origin == ann2.origin)
    a.policy.recv_q[13796][prefix].append(ann3)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)
    a.policy.recv_q[13794][prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)

def test_process_incoming_anns_bgp_path_len():
    """Shorter path length should be preferred when relationship is equal"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(2, 3, 13794),timestamp=0)
    ann2 = Announcement(prefix=prefix, as_path=(2, 13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[2][prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.recv_q[2][prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann2.origin)
    a.policy.recv_q[13796][prefix].append(ann3)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)
    a.policy.recv_q[2][prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)

def test_process_incoming_anns_bgp_seeded():
    """Any incoming announcement should never replace a seeded announcement"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(1,),timestamp=0, seed_asn=1)
    ann1.recv_relationship=Relationships.ORIGIN
    ann2 = Announcement(prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.local_rib[prefix] = ann1
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.recv_q[13795][prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)

def test_process_incoming_anns_bgp_loop_check():
    """An AS should never accept an incoming announcement with its own ASN on the path"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(13796, 1),timestamp=0)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[13796][prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(prefix not in a.policy.local_rib)

def test_process_incoming_withdraw():
    """Test basic processing of incoming withdraw"""
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    ann_w = deepcopy(ann)
    ann_w.withdraw = True
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a.policy.local_rib[prefix].origin == ann.origin)
    a.policy.recv_q[13796][prefix].append(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert announcement is removed from the local rib
    assert(a.policy.local_rib.get(prefix) is None)
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was replaced in local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

def test_process_incoming_withdraw_send_q():
    """Test processing of incoming withdraw when announcement has not yet been sent to neighbors"""
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    ann_w = deepcopy(ann)
    ann_w.withdraw = True
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a.policy.local_rib[prefix].origin == ann.origin)
    # Manually add this to the send queue
    a.policy.send_q[2][prefix].append(a.policy.local_rib[prefix])
    # Withdraw it
    a.policy.recv_q[13796][prefix].append(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert send_q is empty
    assert(len(a.policy.send_q[2][prefix]) == 0)



def test_propagate_bgp_ribs():
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
    as_policies = {asn: BGPRIBSPolicy for asn in
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



