"""Functions to determine customer cone size"""

from bgpy.shared.enums import Relationships

from .base_as import AS


def _get_size_of_and_store_cone(
    self,
    rel_attr: str = Relationships.CUSTOMERS.name.lower(),
    store_cone_asns: bool = False,
) -> None:
    if rel_attr == Relationships.PROVIDERS.name.lower():
        self._get_and_store_provider_cone_and_set_size(store_cone_asns)
    elif rel_attr == Relationships.CUSTOMERS.name.lower():
        self._get_and_store_customer_cone_and_set_size(store_cone_asns)


def _get_and_store_customer_cone_and_set_size(self, store_asns: bool = False) -> None:
    # Recursively assign the customer cone size
    non_edges: list[AS] = []
    cone_dict: dict[int, set[int]] = {}
    for as_obj in self:
        if as_obj.stub or as_obj.multihomed:
            as_obj.customer_cone_size = 0
            cone_dict[as_obj.asn] = set()
            if store_asns:
                as_obj.customer_cone_asns = frozenset()
        else:
            non_edges.append(as_obj)
    for as_obj in non_edges:
        # NOTE: This also updates the cone_dict behind the scenes
        customer_cone: set[int] = self._get_cone_helper(
            as_obj, cone_dict, Relationships.CUSTOMERS.name.lower()
        )
        as_obj.customer_cone_size = len(customer_cone)
        if store_asns:
            as_obj.customer_cone_asns = frozenset(customer_cone)


def _get_and_store_provider_cone_and_set_size(self, store_asns: bool = False) -> None:
    # Recursively assign the provider cone size
    cone_dict: dict[int, set[int]] = {}
    for as_obj in self:
        # NOTE: This also updates the cone_dict behind the scenes
        provider_cone: set[int] = self._get_cone_helper(
            as_obj, cone_dict, Relationships.PROVIDERS.name.lower()
        )
        as_obj.provider_cone_size = len(provider_cone)
        if store_asns:
            as_obj.provider_cone_asns = frozenset(provider_cone)


def _get_cone_helper(
    self,
    as_obj: AS,
    cone_dict: dict[int, set[int]],
    rel_attr: str,
) -> set[int]:
    """Recursively determines the cone size of an as"""

    as_asn = as_obj.asn
    if as_asn in cone_dict:
        return cone_dict[as_asn]
    else:
        cone_dict[as_asn] = set()
        for neighbor in getattr(as_obj, rel_attr):
            cone_dict[as_asn].add(neighbor.asn)
            if neighbor.asn not in cone_dict:
                self._get_cone_helper(neighbor, cone_dict, rel_attr)
            cone_dict[as_asn].update(cone_dict[neighbor.asn])
    return cone_dict[as_asn]


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
    ases = sorted(self, key=lambda x: x.customer_cone_size, reverse=True)
    last_as = ases[0]
    last_as.as_rank = 0
    for i, as_obj in enumerate(ases[1:]):
        if as_obj.customer_cone_size == last_as.customer_cone_size:
            as_obj.as_rank = last_as.as_rank
        else:
            as_obj.as_rank = i

        last_as = as_obj
