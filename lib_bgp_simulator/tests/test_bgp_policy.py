import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships
from ..announcement import Announcement

from ..engine.bgp_as import BGPAS
from ..engine.bgp_policy import BGPPolicy
from ..engine.bgp_ribs_policy import BGPRIBSPolicy
from ..engine.local_rib import LocalRib



@pytest.mark.skip(reason="Must write func to generalize adding to incoming or recvq")
@pytest.mark.parametrize("Policy", [BGPPolicy, BGPRIBSPolicy])
def test_process_incoming_anns_bgp(Policy):
    """Test basic functionality of process_incoming_anns"""
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1)
    a.policy = Policy() 
    a.policy.incoming_anns[prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # assert announcement was accepted to local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

@pytest.mark.skip(reason="Must write func to generalize adding to incoming or recvq")
@pytest.mark.parametrize("Policy", [BGPPolicy, BGPRIBSPolicy])
def test_process_incoming_anns_bgp_duplicate(Policy):
    """sANITy check that duplicated announcements do not cause problems"""
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = Policy()
    a.policy.incoming_anns[prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    a.policy.incoming_anns[prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # assert announcement was accepted to local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

@pytest.mark.skip(reason="Must write func to generalize adding to incoming or recvq")
@pytest.mark.parametrize("Policy", [BGPPolicy, BGPRIBSPolicy])
def test_process_incoming_anns_bgp_relationships(Policy):
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(13794,),timestamp=0)
    ann2 = Announcement(prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = Policy()
    a.policy.incoming_anns[prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.incoming_anns[prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    assert(a.policy.local_rib[prefix].origin == ann2.origin)
    a.policy.incoming_anns[prefix].append(ann3)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)
    a.policy.incoming_anns[prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)

@pytest.mark.skip(reason="Must write func to generalize adding to incoming or recvq")
@pytest.mark.parametrize("Policy", [BGPPolicy, BGPRIBSPolicy])
def test_process_incoming_anns_bgp_path_len(Policy):
    """Shorter path length should be preferred when relationship is equal"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(2, 3, 13794),timestamp=0)
    ann2 = Announcement(prefix=prefix, as_path=(2, 13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = Policy()
    a.policy.incoming_anns[prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.incoming_anns[prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann2.origin)
    a.policy.incoming_anns[prefix].append(ann3)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)
    a.policy.incoming_anns[prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)

@pytest.mark.skip(reason="Must write func to generalize adding to incoming or recvq")
@pytest.mark.parametrize("Policy", [BGPPolicy, BGPRIBSPolicy])
def test_process_incoming_anns_bgp_seeded(Policy):
    """Any incoming announcement should never replace a seeded announcement"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(1,),timestamp=0, seed_asn=1)
    ann1.recv_relationship=Relationships.ORIGIN
    ann2 = Announcement(prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy = Policy()
    a.policy.local_rib[prefix] = ann1
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.incoming_anns[prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)

@pytest.mark.skip(reason="Must write func to generalize adding to incoming or recvq")
@pytest.mark.parametrize("Policy", [BGPPolicy, BGPRIBSPolicy])
def test_process_incoming_anns_bgp_loop_check(Policy):
    """An AS should never accept an incoming announcement with its own ASN on the path"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(13796, 1),timestamp=0)
    a = BGPAS(1) 
    a.policy = Policy()
    a.policy.incoming_anns[prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(prefix not in a.policy.local_rib)
