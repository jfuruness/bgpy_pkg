import pytest


from ...enums import Relationships
from ...announcements import AnnWDefaults

from ...engine import BGPSimpleAS
from ...engine import BGPAS


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
