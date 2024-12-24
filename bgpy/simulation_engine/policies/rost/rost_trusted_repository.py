from dataclasses import dataclass, field

from bgpy.simulation_engine.announcement import Announcement as Ann

TRIE = dict[int, "RoSTTrustedRepoNode"]


@dataclass
class RoSTTrustedRepoNode:
    as_path_branches: TRIE = field(default_factory=dict)
    # End of the path, i.e end of a withdrawal
    # A set of prefixes is used since multiple prefixes may have the same
    # AS-Path. NOTE: this is only for withdrawals, we don't store valid routes
    end_of_as_path_prefixes: set[str] = field(default_factory=set)


class RoSTTrustedRepository:
    """NOTE: this doesn't follow the RoST paper much.

    I have trouble understanding the way the algorithms are written. Once I get
    a better understanding of them I will update this, so I wouldn't rely too closely
    on any internal mechanisms
    """

    def __init__(self) -> None:
        self._withdrawal_as_path_root = RoSTTrustedRepoNode()

    def clear(self) -> None:
        self.__init__()  # type: ignore

    def add_ann(self, ann: Ann) -> None:
        current_node = self._withdrawal_as_path_root
        visited = set()
        for asn in ann.as_path[::-1]:
            if asn in visited:
                raise NotImplementedError("We don't handle path poisoning yet")
            else:
                visited.add(asn)
            if asn not in current_node.as_path_branches:
                if ann.withdraw:
                    new_node = RoSTTrustedRepoNode()
                    current_node.as_path_branches[asn] = new_node
                    current_node = new_node
                else:
                    # withdrawal corresponding to valid route isn't in here,
                    # so there's nothing to do and we should return
                    return

        if ann.withdraw:
            current_node.end_of_as_path_prefixes.add(ann.prefix)
        else:
            # No longer a withdraw
            current_node.end_of_as_path_prefixes.discard(ann.prefix)
            # NOTE: we would also remove stubs from the trie here to be more efficient
            # But that doesn't really matter for this

    def seen_withdrawal(self, ribs_in_ann: Ann) -> bool:
        current_node = self._withdrawal_as_path_root
        for asn in ribs_in_ann.as_path[::-1]:
            current_node = current_node.as_path_branches.get(asn)  # type: ignore
            if current_node is None:
                return False  # type: ignore
            elif ribs_in_ann.prefix in current_node.end_of_as_path_prefixes:
                return True
        return False
