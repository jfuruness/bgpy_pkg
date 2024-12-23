from dataclasses import dataclass

from bgpy.simulation_engine.announcement import Announcement

from .bgp_full_ignore_invalid import BGPFullIgnoreInvalid

@dataclass
class Node:
    branches: dict
    end_of_path: bool


class RoSTTrustedRepository:
    def __init__(self) -> None:
        self._withdrawal_as_path_root = Node(dict(), False)

    def reset(self) -> None:
        self.__init__()

    def add_withdrawal(self, withdraw_ann: Ann) -> None:
        assert withdraw_ann.withdraw is True
        current_node = self._withdrawal_as_path_root
        visited = set()
        for asn in withdraw_ann.as_path:
            if asn in visited:
                raise NotImplementedError("We don't handle path poisoning yet")
            else:
                visited.add(asn)
            if asn not in node.branches:
                current_node.branches[asn] = Node(dict(), False)
                current_node = current_node.branches[asn]
        current_node.end_of_path = True

    def seen_withdrawal(self, ribs_in_ann: Ann) -> bool:
        current_node = self._withdrawal_as_path_root
        for asn in ribs_in_ann.as_path:
            current_node = current_node.branches.get(asn)
            if current_node is None:
                return False
            elif current_node.end_of_path:
                return True
        return False


class RoSTFull(BGPFullIgnoreInvalid):
    """Drops all withdrawals"""

    name = "RoST"

    rost_trusted_repository = RoSTTrustedRepository()

    def seed_ann(self, ann: "Ann") -> None:
        rost_trusted_repository.clear()
        super().seed_ann(ann)

    def process_incoming_anns(self: "BGPFull", *args, **kwargs):
        self.add_withdrawals_to_rost_trusted_repository()
        self.add_suppressed_withdrawals_back_to_recv_q()
        super().process_incoming_anns(*args, **kwargs)

    def add_withdrawals_to_rost_trusted_repository(self) -> None:
        """Adds all incoming withdrawals to recv_q"""

        for prefix, list_of_anns in self.recv_q.items():
            for ann in list_of_anns:
                if ann.withdraw:
                    self.rost_trusted_repository.add_withdrawal(ann)

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
                and self.rost_trusted_repository.seen_withdrawal(ann)
            ):
                self.recv_q.add_ann(ann.copy({"withdraw": True}))
