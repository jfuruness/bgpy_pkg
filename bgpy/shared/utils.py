def collapse_prepending(as_path: tuple[int, ...]) -> tuple[int, ...]:
    """Collapses consecutive duplicate ASNs (prepending) in an AS path

    (1, 1, 2, 3, 3) -> (1, 2, 3). This is not deduplication, so (1, 2, 1) is unchanged.

    Returns the same tuple object if nothing is prepended, which is the common case
    (BGPy itself never prepends), so that case costs one pass and no allocation.

    This lives in shared rather than bgpy/utils since bgpy/utils imports
    the simulation engine, so importing it from a policy would be circular
    """

    for i in range(1, len(as_path)):
        if as_path[i] == as_path[i - 1]:
            break
    else:
        return as_path

    collapsed = list(as_path[:i])
    for asn in as_path[i:]:
        if asn != collapsed[-1]:
            collapsed.append(asn)
    return tuple(collapsed)
