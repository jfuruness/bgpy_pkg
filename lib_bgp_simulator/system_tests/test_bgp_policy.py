from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships
from .run_example import run_example
from ..announcement import Announcement
from .hijack_local_rib import HijackLocalRib
from ..simulator.attacks import SubprefixHijack

from ..engine.bgp_as import BGPAS
from ..engine.bgp_policy import BGPPolicy
from ..engine.bgp_ribs_policy import BGPRIBSPolicy

def test_process_incoming_anns_bgp():
    r"""

    """
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy.incoming_anns[prefix] = list()
    a.policy.incoming_anns[prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # assert announcement was accepted to local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

def test_process_incoming_anns_bgp_duplicate():
    r"""

    """
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy.incoming_anns[prefix] = list()
    a.policy.incoming_anns[prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    a.policy.incoming_anns[prefix] = list()
    print("first", a.policy.local_rib)
    a.policy.incoming_anns[prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    print("second", a.policy.local_rib)
    # assert announcement was accepted to local rib
    assert(a.policy.local_rib[prefix].origin == ann.origin)

def test_process_incoming_anns_bgp_relationships():
    r"""

    """
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix, as_path=(13794,),timestamp=0)
    ann2 = Announcement(prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = Announcement(prefix=prefix, as_path=(13796,),timestamp=0)
    a = BGPAS(1) 
    a.policy.incoming_anns[prefix] = list()
    a.policy.incoming_anns[prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)
    a.policy.incoming_anns[prefix] = list()
    a.policy.incoming_anns[prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    assert(a.policy.local_rib[prefix].origin == ann2.origin)
    a.policy.incoming_anns[prefix] = list()
    a.policy.incoming_anns[prefix].append(ann3)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)


