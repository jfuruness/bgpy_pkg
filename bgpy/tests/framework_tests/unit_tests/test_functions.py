import pytest
from bgpy.as_graphs.base.as_graph.base_as import AS

class DummyPolicy:
    name = "DummyPolicy"

def make_as(asn: int, rank: int = 0):
    """Make AS, you need this to test the functions for customer cones"""
    as_obj = AS(asn=asn, policy=DummyPolicy())
    as_obj.customer_asns = frozenset()
    as_obj.customers = tuple()
    as_obj.customer_cone_size = None
    as_obj.propagation_rank = rank
    return as_obj

def link_customer_provider(parent, child):
    """Parent/Provider to customer relationship"""
    parent.customer_asns |= {child.asn}
    parent.customers = tuple(list(parent.customers) + [child])

def run_customer_cone_logic(as_dict):
    """This traverses the customer cone to ensure logic is correct"""
    max_rank = max(as_obj.propagation_rank for as_obj in as_dict.values())
    
    for rank in range(max_rank + 1):
        for as_obj in as_dict.values():
            if as_obj.propagation_rank == rank:
                cone_asns = set(as_obj.customer_asns)
                for customer_obj in as_obj.customers:
                    if hasattr(customer_obj, "_cone_set"):
                        cone_asns |= customer_obj._cone_set
                
                as_obj._cone_set = cone_asns
                as_obj.customer_cone_size = len(cone_asns)

class TestGetCustomerConeSizeLogic:

    def test_stub_as(self):
        as1 = make_as(1, rank=0)
        run_customer_cone_logic({1: as1})
        assert as1.customer_cone_size == 0

    def test_single_customer(self):
        as1 = make_as(1, rank=1)
        as2 = make_as(2, rank=0)
        link_customer_provider(as1, as2)
        
        run_customer_cone_logic({1: as1, 2: as2})
        assert as1.customer_cone_size == 1
        assert as2.customer_cone_size == 0

    def test_recursive_chain(self):
        as1 = make_as(1, rank=2)
        as2 = make_as(2, rank=1)
        as3 = make_as(3, rank=0)
        link_customer_provider(as1, as2)
        link_customer_provider(as2, as3)
        
        run_customer_cone_logic({1: as1, 2: as2, 3: as3})
        assert as1.customer_cone_size == 2
        assert as2.customer_cone_size == 1

    def test_multihomed_customers(self):
        as1 = make_as(1, rank=2)
        as2 = make_as(2, rank=1)
        as3 = make_as(3, rank=1)
        as4 = make_as(4, rank=0)
        
        link_customer_provider(as1, as2)
        link_customer_provider(as1, as3)
        link_customer_provider(as2, as4)
        link_customer_provider(as3, as4)
        
        run_customer_cone_logic({i: a for i, a in enumerate([as1, as2, as3, as4], 1)})
        assert as1.customer_cone_size == 3
