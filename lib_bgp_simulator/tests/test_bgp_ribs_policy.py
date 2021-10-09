from copy import deepcopy

import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships, ROAValidity
from ..announcement import Announcement

from ..engine import BGPAS
from ..engine import BGPPolicy
from ..engine import BGPRIBSPolicy
from ..engine import LocalRib

def get_prefix_ann_ann_w_a():
    prefix = '137.99.0.0/16'
    ann = Announcement(prefix=prefix,
                       as_path=(13796,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann_w = ann.copy(withdraw=True)
    neighbor = BGPAS(2, peers=[], providers=[], customers=[])
    a = BGPAS(1, peers=[], providers=[], customers=[neighbor])
    neighbor.providers.append(a)
    a.policy = BGPRIBSPolicy()
    return prefix, ann, ann_w, a
 


def test_process_incoming_withdraw():
    """Test basic processing of incoming withdraw"""

    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()

    a.policy.recv_q.add_ann(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a.policy.local_rib.get_ann(prefix).origin == ann.origin)
    a.policy.recv_q.add_ann(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)

    # Assert announcement is removed from the local rib
    assert(a.policy.local_rib.get_ann(prefix) is None)
    a.policy.recv_q.add_ann(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was replaced in local rib
    # NOTE: this test does not work, since withdrawal origin is the same
    assert(a.policy.local_rib.get_ann(prefix).origin == ann.origin)

def test_process_incoming_withdraw_send_q():
    """Test processing of incoming withdraw when announcement has not yet been sent to neighbors"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()

    a.policy.recv_q.add_ann(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a.policy.local_rib.get_ann(prefix).origin == ann.origin)
    assert(a.policy.local_rib.get_ann(prefix).origin == ann.origin)
    # Manually add this to the send queue
    a.policy.send_q.add_ann(2, a.policy.local_rib.get_ann(prefix))
    # Withdraw it
    a.policy.recv_q.add_ann(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    send_info = a.policy.send_q._info[2].get(prefix)
    # Assert send_q is empty
    assert a.policy.send_q._info[2].get(prefix).ann is None

def test_process_incoming_withdraw_ribs_out():
    """Test processing of incoming withdraw when announcement has already been sent to neighbors"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()
    a.policy.recv_q.add_ann(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a.policy.local_rib.get_ann(prefix).origin == ann.origin)
    # Manually add this to the ribs out
    a.policy.ribs_out.add_ann(2, a.policy.local_rib.get_ann(prefix), prefix=prefix)
    # Withdraw it
    a.policy.recv_q.add_ann(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert send_q has withdrawal
    processed_ann_w = a.policy._deep_copy_ann(a, ann_w, Relationships.CUSTOMERS)
    assert a.policy.send_q._info[2][prefix].withdrawal_ann == processed_ann_w

def test_withdraw_best_alternative():
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = Announcement(prefix=prefix,
                       as_path=(13794,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann1_w = ann1.copy(withdraw=True)

    ann2 = Announcement(prefix=prefix,
                       as_path=(13795,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann2_w = ann2.copy(withdraw=True)
 
    ann3 = Announcement(prefix=prefix,
                       as_path=(13796,),
                       timestamp=0,
                       roa_validity=ROAValidity.UNKNOWN,
                       recv_relationship=Relationships.ORIGIN)
    ann3_w = ann3.copy(withdraw=True)
 
    a = BGPAS(1, peers=[], providers=[], customers=[]) 
    a.policy = BGPRIBSPolicy()
    # Populate ribs_in with three announcements
    a.policy.recv_q.add_ann(ann1)
    a.policy.process_incoming_anns(a, Relationships.PROVIDERS)
    a.policy.recv_q.add_ann(ann2)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    a.policy.recv_q.add_ann(ann3)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)

    assert(a.policy.local_rib.get_ann(prefix).origin == ann3.origin)


    # Withdraw ann3, now AS should use ann2'
    a.policy.recv_q.add_ann(ann3_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    assert(a.policy.local_rib.get_ann(prefix).origin == ann2.origin)
    # Withdraw ann2, now AS should use ann1
    a.policy.recv_q.add_ann(ann2_w)
    a.policy.process_incoming_anns(a, Relationships.PEERS)
    assert(a.policy.local_rib.get_ann(prefix).origin == ann1.origin)

def test_withdraw_seeded():
    """Customers > Peers > Providers"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()
    # Populate ribs_in with an announcement
    a.policy.recv_q.add_ann(ann)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    a.policy.local_rib.get_ann(prefix).seed_asn = 1
    # Withdraw ann
    a.policy.recv_q.add_ann(ann_w)
    a.policy.process_incoming_anns(a, Relationships.CUSTOMERS)
    # Assert ann is still there
    assert(a.policy.local_rib.get_ann(prefix).origin == ann.origin)
