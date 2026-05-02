import pytest
from bgpy.as_graphs.base.as_graph.base_as import AS
from bgpy.as_graphs.base.as_graph.customer_cone_funcs import (
    _get_customer_cone_size,
    _get_cone_size_helper
)

class DummyPolicy:
    name = "DummyPolicy"

def make_as(asn: int, rank: int = 0):
    """Make AS, you need this to test the functions for customer cones"""
    as_obj = AS(asn=asn, policy=DummyPolicy())
    as_obj.customer_asns = frozenset()
    as_obj.customers = tuple()
    as_obj.customer_cone_size = None
    as_obj.propagation_rank = rank
    
    """Stub means an edge with no customers"""
    @property
    def stub(self):
        return len(self.customers) == 0
    
    """Returns nothing for this test"""
    @property
    def multihomed(self):
        return False

    type(as_obj).stub = stub
    type(as_obj).multihomed = multihomed
    return as_obj

def link_customer_provider(parent, child):
    parent.customer_asns |= {child.asn}
    parent.customers = tuple(list(parent.customers) + [child])

class MockGraph:
    """This is a 'mock' graph required by the _get_customer_cone_size function and what it expects"""
    def __init__(self, as_dict):
        self.as_dict = as_dict

    def __iter__(self):
        return iter(self.as_dict.values())

    def _get_customer_cone_size(self):
        return _get_customer_cone_size(self)

    def _get_cone_size_helper(self, as_obj, cone_dict):
        return _get_cone_size_helper(self, as_obj, cone_dict)

class TestGetCustomerConeSizeLogic:

    def test_stub_as(self):
        """This test basically ensures there is nothing"""
        as1 = make_as(1, rank=0)
        graph = MockGraph({1: as1})
        
        graph._get_customer_cone_size()
        assert as1.customer_cone_size == 0

    def test_single_customer(self):
        as1 = make_as(1, rank=1)
        as2 = make_as(2, rank=0)
        link_customer_provider(as1, as2)
        
        graph = MockGraph({1: as1, 2: as2})
        graph._get_customer_cone_size()
        
        assert as1.customer_cone_size == 1

    def test_recursive_chain(self):
        """Tests recursion"""
        as1 = make_as(1, rank=2)
        as2 = make_as(2, rank=1)
        as3 = make_as(3, rank=0)
        link_customer_provider(as1, as2)
        link_customer_provider(as2, as3)
        
        graph = MockGraph({1: as1, 2: as2, 3: as3})
        graph._get_customer_cone_size()
        
        assert as1.customer_cone_size == 2
        assert as2.customer_cone_size == 1

    def test_multihomed_customers(self):
        """Tests multiple provide->customers relationships, each customer should be counted once"""
        as1 = make_as(1, rank=2)
        as2 = make_as(2, rank=1)
        as3 = make_as(3, rank=1)
        as4 = make_as(4, rank=0)
        
        link_customer_provider(as1, as2)
        link_customer_provider(as1, as3)
        link_customer_provider(as2, as4)
        link_customer_provider(as3, as4)
        
        graph = MockGraph({1: as1, 2: as2, 3: as3, 4: as4})
        graph._get_customer_cone_size()
        
        assert as1.customer_cone_size == 3
