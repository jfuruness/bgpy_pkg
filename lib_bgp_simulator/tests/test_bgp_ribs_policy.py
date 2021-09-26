from copy import deepcopy

import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships, ROAValidity
from ..announcement import Announcement

from ..engine.bgp_as import BGPAS
from ..engine.bgp_policy import BGPPolicy
from ..engine.bgp_ribs_policy import BGPRIBSPolicy
from ..engine.local_rib import LocalRib

def get_prefix_ann_ann_w_a():
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix,
                       as_path=(13796,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann_w = ann.copy_w_sim_attrs(withdraw=True)
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    return prefix, ann, ann_w, a
 


def test_process_incoming_withdraw():
    """Test basic processing of incoming withdraw"""

    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()

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
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()

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

def test_process_incoming_withdraw_ribs_out():
    """Test processing of incoming withdraw when announcement has already been sent to neighbors"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a.policy.local_rib[prefix].origin == ann.origin)
    # Manually add this to the ribs out
    a.policy.ribs_out[2][prefix] = a.policy.local_rib[prefix]
    # Withdraw it
    a.policy.recv_q[13796][prefix].append(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert send_q has withdrawal
    assert(len(a.policy.send_q[2][prefix]) == 1)

def test_withdraw_best_alternative():
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix,
                       as_path=(13794,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann1_w = ann1.copy_w_sim_attrs(withdraw=True)

    ann2 = Announcement(prefix=prefix,
                       as_path=(13795,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann2_w = ann2.copy_w_sim_attrs(withdraw=True)
 
    ann3 = Announcement(prefix=prefix,
                       as_path=(13796,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann3_w = ann3.copy_w_sim_attrs(withdraw=True)
 
    a = BGPAS(1) 
    a.policy = BGPRIBSPolicy()
    # Populate ribs_in with three announcements
    a.policy.recv_q[13794][prefix].append(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    a.policy.recv_q[13795][prefix].append(ann2)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    a.policy.recv_q[13796][prefix].append(ann3)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann3.origin)
    # Withdraw ann3, now AS should use ann2
    a.policy.recv_q[13796][prefix].append(ann3_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib[prefix].origin == ann2.origin)
    # Withdraw ann2, now AS should use ann1
    a.policy.recv_q[13795][prefix].append(ann2_w)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    assert(a.policy.local_rib[prefix].origin == ann1.origin)

def test_withdraw_seeded():
    """Customers > Peers > Providers"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()
    # Populate ribs_in with an announcement
    a.policy.recv_q[13796][prefix].append(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    a.policy.local_rib[prefix].seed_asn = 1
    # Withdraw ann
    a.policy.recv_q[13796][prefix].append(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann is still there
    assert(a.policy.local_rib[prefix].origin == ann.origin)
