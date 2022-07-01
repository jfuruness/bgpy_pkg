import pytest
from ...enums import Relationships
from ...announcements import AnnWDefaults

from ...engine import BGPAS


def get_prefix_ann_ann_w_a():
    prefix = '137.99.0.0/16'
    ann = AnnWDefaults(prefix=prefix,
                       as_path=(13796,),
                       timestamp=0,
                       recv_relationship=Relationships.ORIGIN)
    ann_w = ann.copy(withdraw=True)
    neighbor = BGPAS(2, peers=[], providers=[], customers=[])
    a = BGPAS(1, peers=[], providers=[], customers=[neighbor])
    neighbor.providers.append(a)
    return prefix, ann, ann_w, a


@pytest.mark.skip
def test_process_incoming_withdraw():
    """Test basic processing of incoming withdraw"""

    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()

    a._recv_q.add_ann(ann)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a._local_rib.get_ann(prefix).origin == ann.origin)
    a._recv_q.add_ann(ann_w)
    a.process_incoming_anns(Relationships.CUSTOMERS)

    # Assert announcement is removed from the local rib
    assert(a._local_rib.get_ann(prefix) is None)
    a._recv_q.add_ann(ann)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # Assert ann was replaced in local rib
    # NOTE: this test does not work, since withdrawal origin is the same
    assert(a._local_rib.get_ann(prefix).origin == ann.origin)


@pytest.mark.skip
def test_process_incoming_withdraw_send_q():
    """Test processing of incoming withdraw

    when announcement has not yet been sent to neighbors"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()

    a._recv_q.add_ann(ann)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a._local_rib.get_ann(prefix).origin == ann.origin)
    assert(a._local_rib.get_ann(prefix).origin == ann.origin)
    # Manually add this to the send queue
    a._send_q.add_ann(2, a._local_rib.get_ann(prefix))
    # Withdraw it
    a._recv_q.add_ann(ann_w)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    a._send_q._info[2].get(prefix)
    # Assert _send_q is empty
    assert a._send_q._info[2].get(prefix).ann is None


@pytest.mark.skip
def test_process_incoming_withdraw_ribs_out():
    """Test processing of incoming withdraw

    when announcement has already been sent to neighbors"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()
    a._recv_q.add_ann(ann)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # Assert ann was received
    assert(a._local_rib.get_ann(prefix).origin == ann.origin)
    # Manually add this to the ribs out
    a._ribs_out.add_ann(2, a._local_rib.get_ann(prefix))
    # Withdraw it
    a._recv_q.add_ann(ann_w)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # Assert _send_q has withdrawal
    processed_ann_w = a._copy_and_process(ann_w, Relationships.CUSTOMERS)
    assert a._send_q._info[2][prefix].withdrawal_ann == processed_ann_w


@pytest.mark.skip
def test_withdraw_best_alternative():
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix,
                        as_path=(13794,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)
    ann1.copy(withdraw=True)

    ann2 = AnnWDefaults(prefix=prefix,
                        as_path=(13795,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)
    ann2_w = ann2.copy(withdraw=True)

    ann3 = AnnWDefaults(prefix=prefix,
                        as_path=(13796,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)
    ann3_w = ann3.copy(withdraw=True)

    a = BGPAS(1, peers=[], providers=[], customers=[])
    # Populate _ribs_in with three announcements
    a._recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    a._recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PEERS)
    a._recv_q.add_ann(ann3)
    a.process_incoming_anns(Relationships.CUSTOMERS)

    assert(a._local_rib.get_ann(prefix).origin == ann3.origin)

    # Withdraw ann3, now AS should use ann2'
    a._recv_q.add_ann(ann3_w)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert(a._local_rib.get_ann(prefix).origin == ann2.origin)
    # Withdraw ann2, now AS should use ann1
    a._recv_q.add_ann(ann2_w)
    a.process_incoming_anns(Relationships.PEERS)
    assert(a._local_rib.get_ann(prefix).origin == ann1.origin)


@pytest.mark.skip
def test_withdraw_seeded():
    """Customers > Peers > Providers"""
    prefix, ann, ann_w, a = get_prefix_ann_ann_w_a()
    # Populate _ribs_in with an announcement
    a._recv_q.add_ann(ann)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    a._local_rib.get_ann(prefix).seed_asn = 1
    # Withdraw ann
    a._recv_q.add_ann(ann_w)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # Assert ann is still there
    assert(a._local_rib.get_ann(prefix).origin == ann.origin)


@pytest.mark.skip
def test_withdraw_sending():
    """Test AS sending of the correct withdrawals when a better ann is received

    a
    |
    b

    """
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix,
                        as_path=(13794,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)

    ann2 = AnnWDefaults(prefix=prefix,
                        as_path=(13795,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)

    b = BGPAS(2, peers=[], providers=[], customers=[])
    a = BGPAS(1, peers=[], providers=[], customers=[b])
    # round 1
    a._recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    a.propagate_to_customers()
    b.process_incoming_anns(Relationships.PROVIDERS)
    # round 2
    a._recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PEERS)
    a.propagate_to_customers()
    b.process_incoming_anns(Relationships.PROVIDERS)

    assert(b._local_rib.get_ann(prefix).origin == ann2.origin)


@pytest.mark.skip
def test_withdraw_sending_multihop():
    """Test propagation of withdrawals

    a
    |
    b
    |
    c

    """
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix,
                        as_path=(13794,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)

    ann2 = AnnWDefaults(prefix=prefix,
                        as_path=(13795,),
                        timestamp=0,
                        recv_relationship=Relationships.ORIGIN)

    c = BGPAS(3, peers=[], providers=[], customers=[])
    b = BGPAS(2, peers=[], providers=[], customers=[c])
    a = BGPAS(1, peers=[], providers=[], customers=[b])
    # round 1
    a._recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    a.propagate_to_customers()
    b.process_incoming_anns(Relationships.PROVIDERS)
    b.propagate_to_customers()
    c.process_incoming_anns(Relationships.PROVIDERS)

    # round 2
    a._recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PEERS)
    a.propagate_to_customers()
    b.process_incoming_anns(Relationships.PROVIDERS)
    b.propagate_to_customers()
    print('c ribns in', c._recv_q.prefix_anns())
    c.process_incoming_anns(Relationships.PROVIDERS)

    assert(c._local_rib.get_ann(prefix).origin == ann2.origin)
