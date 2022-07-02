import pytest


from ...enums import Relationships
from ...announcements import AnnWDefaults

from ...engine import BGPSimpleAS
from ...engine import BGPAS


@pytest.mark.parametrize("BaseASCls", [BGPSimpleAS, BGPAS])
def test_process_incoming_anns_bgp_relationships(BaseASCls):
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix, as_path=(13794,), timestamp=0)
    ann2 = AnnWDefaults(prefix=prefix, as_path=(13795,), timestamp=0)
    ann3 = AnnWDefaults(prefix=prefix, as_path=(13796,), timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[])
    a._recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a._local_rib.get_ann(prefix).origin == ann1.origin)
    a._recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PEERS)
    assert(a._local_rib.get_ann(prefix).origin == ann2.origin)
    a._recv_q.add_ann(ann3)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert(a._local_rib.get_ann(prefix).origin == ann3.origin)


@pytest.mark.parametrize("BaseASCls", [BGPSimpleAS, BGPAS])
def test_process_incoming_anns_bgp_path_len(BaseASCls):
    """Shorter path length should be preferred when relationship is equal"""
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix, as_path=(2, 3, 13794), timestamp=0)
    ann2 = AnnWDefaults(prefix=prefix, as_path=(20, 13795,), timestamp=0)
    ann3 = AnnWDefaults(prefix=prefix, as_path=(13796,), timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[])
    a._recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a._local_rib.get_ann(prefix).origin == ann1.origin)
    a._recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a._local_rib.get_ann(prefix).origin == ann2.origin)
    a._recv_q.add_ann(ann3)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a._local_rib.get_ann(prefix).origin == ann3.origin)


@pytest.mark.parametrize("BaseASCls", [BGPSimpleAS, BGPAS])
def test_process_incoming_anns_bgp_seeded(BaseASCls):
    """Any incoming announcement should never replace a seeded announcement"""
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix, as_path=(1,), timestamp=0, seed_asn=1)
    ann1.recv_relationship = Relationships.ORIGIN
    ann2 = AnnWDefaults(prefix=prefix, as_path=(13795,), timestamp=0)
    AnnWDefaults(prefix=prefix, as_path=(13796,), timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[])
    a._local_rib.add_ann(ann1)
    assert(a._local_rib.get_ann(prefix).origin == ann1.origin)
    a._recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert(a._local_rib.get_ann(prefix).origin == ann1.origin)


@pytest.mark.parametrize("BaseASCls", [BGPSimpleAS, BGPAS])
def test_process_incoming_anns_bgp_loop_check(BaseASCls):
    """An AS should never accept an incoming announcement

    with its own ASN on the path"""
    prefix = '137.99.0.0/16'
    ann1 = AnnWDefaults(prefix=prefix, as_path=(13796, 1), timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[])
    a._recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert a._local_rib.get_ann(prefix) is None
