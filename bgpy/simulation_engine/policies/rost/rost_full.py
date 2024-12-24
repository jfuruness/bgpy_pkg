from dataclasses import dataclass, field

from bgpy.simulation_engine.announcement import Announcement

from .bgp_full_ignore_invalid import BGPFullIgnoreInvalid


@dataclass
class RoSTTrustedRepoNode:
    as_path_branches: dict = field(default_factory=dict)
    # End of the path, i.e end of a withdrawal
    # A set of prefixes is used since multiple prefixes may have the same
    # AS-Path. NOTE: this is only for withdrawals, we don't store valid routes
    end_of_as_path_prefixes: set = field(default_factory=set)


class RoSTTrustedRepository:
    """NOTE: this doesn't follow the RoST paper much.

    I have trouble understanding the way the algorithms are written. Once I get
    a better understanding of them I will update this, so I wouldn't rely too closely
    on any internal mechanisms
    """

    def __init__(self) -> None:
        self._withdrawal_as_path_root = RoSTTrustedRepoNode()

    def reset(self) -> None:
        self.__init__()

    def add_ann(self, ann: Ann) -> None:
        current_node = self._withdrawal_as_path_root
        visited = set()
        for asn in ann.as_path:
            if asn in visited:
                raise NotImplementedError("We don't handle path poisoning yet")
            else:
                visited.add(asn)
            if asn not in node.as_path_branches:
                if ann.withdraw:
                    new_node = RoSTTrustedRepoNode()
                    current_node.as_path_branches[asn] = new_node
                    current_node = new_node
                else:
                    # withdrawal corresponding to valid route isn't in here,
                    # so there's nothing to do and we should return
                    return

        if ann.withdraw:
            current_node.end_of_path_prefixes.add(ann.prefix)
        else:
            # No longer a withdraw
            current_node.end_of_path_prefixes.remove(ann.prefix)
            # NOTE: we would also remove stubs from the trie here to be more efficient
            # But that doesn't really matter for this

    def seen_withdrawal(self, ribs_in_ann: Ann) -> bool:
        current_node = self._withdrawal_as_path_root
        for asn in ribs_in_ann.as_path:
            current_node = current_node.as_path_branches.get(asn)
            if current_node is None:
                return False
            elif ribs_in_ann.prefix in current_node.end_of_path_prefixes:
                return True
        return False


class RoSTFull(BGPFullIgnoreInvalid):
    """Drops all withdrawals"""

    name = "RoST"

    rost_trusted_repository = RoSTTrustedRepository()

    def __init__(self, *args, **kwargs) -> None:
        rost_trusted_repository.clear()
        super().__init__(*args, **kwargs)

    def withdraw_ann_from_neighbors(self, withdraw_ann: Ann) -> None:
        """Adds withdrawals you create to RoST Trusted Repo"""

        self.rost_trusted_repository.add_ann(ann)
        super().withdraw_ann_from_neighbors(withdraw_ann)

    def process_incoming_anns(self, *args, **kwargs):
        """Adds withdrawals and anns you recieved to RoST trusted Repo"""

        self.add_recv_q_to_rost_trusted_repository()
        self.add_suppressed_withdrawals_back_to_recv_q()
        super().process_incoming_anns(*args, **kwargs)

    def add_recv_q_to_rost_trusted_repository(self) -> None:
        """Adds all incoming withdrawals to recv_q"""

        for prefix, list_of_anns in self.recv_q.items():
            for ann in list_of_anns:
                self.rost_trusted_repository.add_ann(ann)

    def add_suppressed_withdrawals_back_to_recv_q(self) -> None:
        for ann_info in self.ribs_in.get_ann_infos():
            ribs_in_ann = ann_info.unprocessed_ann

            # Determine if the RIBsIn ann is already being withdrawn
            withdrawal_in_recv_q = False
            for ann in self.recv_q.get(ann.prefix, []):
                if ribs_in_ann.as_path == ann.as_path:
                    withdrawal_in_recv_q = True

            # if ribs_in_ann withdrawal not in the recv_q,
            # and ribs_in_ann in the trusted repo, create a withdrawal
            if (
                not withdrawal_in_recv_q
                and self.rost_trusted_repository.seen_withdrawal(ribs_in_ann)
            ):
                self.recv_q.add_ann(ribs_in_ann.copy({"withdraw": True}))
