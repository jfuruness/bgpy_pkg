"""Functions to determine customer and provider cones"""

from bgpy.enums import Relationships

from .base_as import AS


def _set_provider_cone_asns(self) -> None:
    """Sets provider cones"""

    cone_dict: dict[int, set[int]] = {}
    for as_obj in self:
        provider_cone_asns: set[int] = self._get_cone_helper(
            as_obj, cone_dict, Relationships.PROVIDERS
        )
        as_obj.provider_cone_asns = frozenset(provider_cone_asns)


def _set_customer_cone_asns(self) -> None:
    """Sets customer cone"""

    # Recursively assign the customer cone size
    non_edges: list[AS] = []
    cone_dict: dict[int, set[int]] = {}
    # Hack for speed
    for as_obj in self:
        if as_obj.stub or as_obj.multihomed:
            as_obj.customer_cone_asns = frozenset()
            cone_dict[as_obj.asn] = set()
        else:
            non_edges.append(as_obj)
    for as_obj in non_edges:
        customer_cone_asns: set[int] = self._get_cone_helper(
            as_obj, cone_dict, Relationships.CUSTOMERS
        )
        as_obj.customer_cone_asns = frozenset(customer_cone_asns)


def _get_cone_helper(
    self, as_obj: AS, cone_dict: dict[int, set[int]], rel: Relationships
) -> set[int]:
    """Recursively determines the cone size of an as"""

    if as_obj.asn in cone_dict:
        return cone_dict[as_obj.asn]
    else:
        cone_dict[as_obj.asn] = set()
        if rel == Relationships.CUSTOMERS:
            rel_neighbors = as_obj.customers
        elif rel == Relationships.PROVIDERS:
            rel_neighbors = as_obj.providers
        else:
            raise NotImplementedError
        for neighbor_as in rel_neighbors:
            cone_dict[as_obj.asn].add(neighbor_as.asn)
            self._get_cone_helper(neighbor_as, cone_dict, rel)
            cone_dict[as_obj.asn].update(cone_dict[neighbor_as.asn])
    return cone_dict[as_obj.asn]


def _get_as_rank(self) -> None:
    """Calculate the AS rank

    ASRank is owned by CAIDA, so one would assume that their
    serial-2 datasets are the same as their AS Rank relationships

    They calculate AS Rank based on just the customer cone size, as seen
    here under the AS Rank header:
    https://asrank.caida.org/about

    The one caveat is that if two ASes have the same customer cone size,
    they have the same AS rank, but then the next AS will have a rank as
    if the sequence never stopped incrementing.
    For example:

    ASN1: cone size 100: AS Rank 1
    ASN2: cone size 100: AS Rank 1
    ASN3: cone size 99: AS Rank 3

    In this example, ASN3 has a AS Rank of 3, because even though there is no AS
    with a rank of 2, the sequence continues even if there are ties

    All of this is documented at the URL above
    """

    # Highest customer cone size first
    ases = list(sorted(self, key=lambda x: x.customer_cone_size, reverse=True))
    last_as = ases[0]
    last_as.as_rank = 0
    for i, as_obj in enumerate(ases[1:]):
        if as_obj.customer_cone_size == last_as.customer_cone_size:
            as_obj.as_rank = last_as.as_rank
        else:
            as_obj.as_rank = i

        last_as = as_obj
