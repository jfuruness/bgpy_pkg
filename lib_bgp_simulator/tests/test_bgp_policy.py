import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..enums import ASNs, Relationships, ROAValidity
from ..announcement import Announcement

from ..engine import BGPAS
from ..engine import BGPRIBsAS
from ..engine import LocalRib


class EasyAnn(Announcement):
    __slots__ = []
    def __init__(self,
                 _prefix=None,
                 as_path=None,
                 timestamp=0,
                 seed_asn=None,
                 roa_validity=ROAValidity.UNKNOWN,
                 recv_relationship=Relationships.CUSTOMERS,
                 withdraw=False,
                 traceback_end=False):
        super(EasyAnn, self).__init__(_prefix,
                                      as_path=as_path,
                                      timestamp=timestamp,
                                      seed_asn=seed_asn,
                                      roa_validity=roa_validity,
                                      recv_relationship=recv_relationship,
                                      withdraw=withdraw,
                                      traceback_end=traceback_end)


@pytest.mark.parametrize("BaseASCls", [BGPAS, BGPRIBsAS])
def test_process_incoming_anns_bgp(BaseASCls):
    """Test basic functionality of process_incoming_anns"""
    prefix = '137.99.0.0/16'
    ann = EasyAnn(_prefix=prefix, as_path=(13796,),timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[])
    a.recv_q.add_ann(ann)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    # assert announcement was accepted to local rib
    assert(a.local_rib.get_ann(prefix).origin == ann.origin)

@pytest.mark.parametrize("BaseASCls", [BGPAS, BGPRIBsAS])
def test_process_incoming_anns_bgp_relationships(BaseASCls):
    """Customers > Peers > Providers"""
    prefix = '137.99.0.0/16'
    ann1 = EasyAnn(_prefix=prefix, as_path=(13794,),timestamp=0)
    ann2 = EasyAnn(_prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = EasyAnn(_prefix=prefix, as_path=(13796,),timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[]) 
    a.recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a.local_rib.get_ann(prefix).origin == ann1.origin)
    a.recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PEERS)
    assert(a.local_rib.get_ann(prefix).origin == ann2.origin)
    a.recv_q.add_ann(ann3)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert(a.local_rib.get_ann(prefix).origin == ann3.origin)

@pytest.mark.parametrize("BaseASCls", [BGPAS, BGPRIBsAS])
def test_process_incoming_anns_bgp_path_len(BaseASCls):
    """Shorter path length should be preferred when relationship is equal"""
    prefix = '137.99.0.0/16'
    ann1 = EasyAnn(_prefix=prefix, as_path=(2, 3, 13794),timestamp=0)
    ann2 = EasyAnn(_prefix=prefix, as_path=(20, 13795,),timestamp=0)
    ann3 = EasyAnn(_prefix=prefix, as_path=(13796,),timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[]) 
    a.recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a.local_rib.get_ann(prefix).origin == ann1.origin)
    a.recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a.local_rib.get_ann(prefix).origin == ann2.origin)
    a.recv_q.add_ann(ann3)
    a.process_incoming_anns(Relationships.PROVIDERS)
    assert(a.local_rib.get_ann(prefix).origin == ann3.origin)

@pytest.mark.parametrize("BaseASCls", [BGPAS, BGPRIBsAS])
def test_process_incoming_anns_bgp_seeded(BaseASCls):
    """Any incoming announcement should never replace a seeded announcement"""
    prefix = '137.99.0.0/16'
    ann1 = EasyAnn(_prefix=prefix, as_path=(1,),timestamp=0, seed_asn=1)
    ann1.recv_relationship=Relationships.ORIGIN
    ann2 = EasyAnn(_prefix=prefix, as_path=(13795,),timestamp=0)
    ann3 = EasyAnn(_prefix=prefix, as_path=(13796,),timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[]) 
    a.local_rib.add_ann(ann1, prefix=prefix)
    assert(a.local_rib.get_ann(prefix).origin == ann1.origin)
    a.recv_q.add_ann(ann2)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert(a.local_rib.get_ann(prefix).origin == ann1.origin)

@pytest.mark.parametrize("BaseASCls", [BGPAS, BGPRIBsAS])
def test_process_incoming_anns_bgp_loop_check(BaseASCls):
    """An AS should never accept an incoming announcement with its own ASN on the path"""
    prefix = '137.99.0.0/16'
    ann1 = EasyAnn(_prefix=prefix, as_path=(13796, 1),timestamp=0)
    a = BaseASCls(1, peers=[], providers=[], customers=[]) 
    a.recv_q.add_ann(ann1)
    a.process_incoming_anns(Relationships.CUSTOMERS)
    assert a.local_rib.get_ann(prefix) is None