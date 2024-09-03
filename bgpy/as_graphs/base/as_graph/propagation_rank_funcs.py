"""Functions to create ranks for propagation"""

from .base_as import AS


def _assign_propagation_ranks(self):
    """Assigns propagation ranks from the leafs to input_clique"""

    for as_obj in self:
        self._assign_ranks_helper(as_obj, 0)


def _assign_ranks_helper(self, as_obj: AS, rank: int):
    """Assigns ranks to all ases in customer/provider chain recursively"""

    if as_obj.propagation_rank is None or as_obj.propagation_rank < rank:
        as_obj.propagation_rank = rank
        # Only update it's providers if it's rank becomes higher
        # This avoids a double for loop of writes
        for provider_obj in as_obj.providers:
            self._assign_ranks_helper(provider_obj, rank + 1)


def _get_propagation_ranks(self) -> tuple[tuple[AS, ...], ...]:
    """Orders ASes by rank"""

    max_rank: int = max(x.propagation_rank for x in self)
    # Create a list of empty lists
    # Ignore types here for speed purposes
    ranks: list[list[AS]] = [list() for _ in range(max_rank + 1)]
    # Append the ASes into their proper rank
    for as_obj in self:
        ranks[as_obj.propagation_rank].append(as_obj)

    # Create tuple ranks
    return tuple([tuple(sorted(rank)) for rank in ranks])
