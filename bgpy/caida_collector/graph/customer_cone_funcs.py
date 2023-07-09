"""Functions to determine customer cone size"""

from .base_as import AS


def _get_customer_cone_size(self):
    """Gets the AS rank by customer cone, the same way Caida does it"""

    # Recursively assign the customer cone size
    non_edges: list[AS] = []
    cone_dict: dict[int, set[int]] = {}
    for as_obj in self:
        if as_obj.stub or as_obj.multihomed:
            as_obj.customer_cone_size = 0
            cone_dict[as_obj.asn] = set()
        else:
            non_edges.append(as_obj)
    for as_obj in non_edges:
        customer_cone: set[int] = self._get_cone_size_helper(as_obj, cone_dict)
        as_obj.customer_cone_size = len(customer_cone)


def _get_cone_size_helper(self, as_obj: AS, cone_dict: dict[int, set[int]]) -> set[int]:
    """Recursively determines the cone size of an as"""

    if as_obj.asn in cone_dict:
        return cone_dict[as_obj.asn]
    else:
        cone_dict[as_obj.asn] = set()
        for customer in as_obj.customers:
            cone_dict[as_obj.asn].add(customer.asn)
            self._get_cone_size_helper(customer, cone_dict)
            cone_dict[as_obj.asn].update(cone_dict[customer.asn])
    return cone_dict[as_obj.asn]
