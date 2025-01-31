from dataclasses import dataclass, field

from bgpy.simulation_engine.announcement import Announcement as Ann

TRIE = dict[int, "RoSTTrustedRepoNode"]


@dataclass
class RoSTTrustedRepoNode:
    as_path_branches: TRIE = field(default_factory=dict)
    # End of the path, i.e end of a withdrawal
    # A set of prefixes is used since multiple prefixes may have the same
    # AS-Path. NOTE: this is only for withdrawals, we don't store valid routes

    # NOTE: Had to add the as-path here to account for routing loops that need
    # to be withdrawn
    end_of_as_path_prefixes: set[tuple[str, tuple[int, ...]]] = field(
        default_factory=set
    )

    def __repr__(self, depth=0) -> str:
        indent = "  " * depth
        result = f"{indent}Node(EndPrefixes: {self.end_of_as_path_prefixes})\n"
        for asn, node in self.as_path_branches.items():
            result += f"{indent}  ASN {asn}:\n{node.__repr__(depth + 2)}"
        return result


class RoSTTrustedRepository:
    """NOTE: this doesn't follow the RoST paper much.

    I have trouble understanding the way the algorithms are written. Once I get
    a better understanding of them I will update this, so I wouldn't rely too closely
    on any internal mechanisms
    """

    def __init__(self) -> None:
        self._withdrawal_as_path_root = RoSTTrustedRepoNode()

    def __repr__(self) -> str:
        return f"RoSTTrustedRepository:\n{self._withdrawal_as_path_root.__repr__()}"

    def clear(self) -> None:
        self.__init__()  # type: ignore

    def add_ann(self, ann: Ann) -> None:
        key = (ann.prefix, ann.as_path)
        current_node = self._withdrawal_as_path_root
        for asn in ann.as_path[::-1]:
            if asn not in current_node.as_path_branches:
                if ann.withdraw:
                    new_node = RoSTTrustedRepoNode()
                    current_node.as_path_branches[asn] = new_node
                    current_node = new_node
                else:
                    # withdrawal corresponding to valid route isn't in here,
                    # so there's nothing to do and we should return
                    return
            else:
                current_node = current_node.as_path_branches[asn]

        if ann.withdraw:
            current_node.end_of_as_path_prefixes.add(key)
        else:
            # No longer a withdraw
            current_node.end_of_as_path_prefixes.discard(key)
            # NOTE: we would also remove stubs from the trie here to be more efficient
            # But that doesn't really matter for this

    def seen_withdrawal(self, ribs_in_ann: Ann, checking_asn: int) -> bool:
        current_node = self._withdrawal_as_path_root
        as_path_thus_far: list[int] = list()
        for asn in [checking_asn, *ribs_in_ann.as_path][::-1]:
            as_path_thus_far.insert(0, asn)
            current_node = current_node.as_path_branches.get(asn)  # type: ignore
            if current_node is None:
                return False  # type: ignore
            elif (
                ribs_in_ann.prefix,
                tuple(as_path_thus_far),
            ) in current_node.end_of_as_path_prefixes:
                return True
        return False
