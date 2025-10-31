"""Functions to determine max customer depth and provider depth"""

from bgpy.shared.enums import Relationships

from .base_as import AS


def _get_and_store_depths(self) -> None:
    """Compute the maximum customer depth and provider depth for each AS."""
    customer_depth_cache: dict[int, int] = {}
    provider_depth_cache: dict[int, int] = {}

    for as_obj in self:
        as_obj.max_customer_depth = _get_max_depth_helper(
            self, as_obj, Relationships.CUSTOMERS.name.lower(), customer_depth_cache
        )
        as_obj.max_provider_depth = _get_max_depth_helper(
            self, as_obj, Relationships.PROVIDERS.name.lower(), provider_depth_cache
        )


def _get_max_depth_helper(
    self,
    as_obj: AS,
    rel_attr: str,
    cache: dict[int, int],
) -> int:
    """Recursively determines the maximum depth of an AS to its leaves along a relationship."""

    as_asn = as_obj.asn
    if as_asn in cache:
        return cache[as_asn]

    neighbors = getattr(as_obj, rel_attr)
    if not neighbors:
        # Leaf node: depth = 0
        cache[as_asn] = 0
        return 0

    # Recursively compute the max depth of each neighbor
    max_depth = 0
    for neighbor in neighbors:
        depth = 1 + _get_max_depth_helper(self, neighbor, rel_attr, cache)
        if depth > max_depth:
            max_depth = depth

    cache[as_asn] = max_depth
    return max_depth
