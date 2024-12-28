from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.simulation_engine.policies.bgp import BGPFullIgnoreInvalid

from .rost_trusted_repository import RoSTTrustedRepository


class RoSTFull(BGPFullIgnoreInvalid):
    """Drops all withdrawals"""

    name = "RoST Full"

    rost_trusted_repository = RoSTTrustedRepository()

    def __init__(self, *args, **kwargs) -> None:
        self.rost_trusted_repository.clear()
        super().__init__(*args, **kwargs)

    def withdraw_ann_from_neighbors(self, withdraw_ann: Ann) -> None:
        """Adds withdrawals you create to RoST Trusted Repo"""

        self.rost_trusted_repository.add_ann(withdraw_ann)
        super().withdraw_ann_from_neighbors(withdraw_ann)

    def process_incoming_anns(self, *args, **kwargs):
        """Adds withdrawals and anns you recieved to RoST trusted Repo"""

        self.add_recv_q_to_rost_trusted_repository()
        self.remove_anns_from_recv_q_that_should_be_withdrawn()
        self.add_suppressed_withdrawals_back_to_recv_q(*args, **kwargs)
        super().process_incoming_anns(*args, **kwargs)

    def add_recv_q_to_rost_trusted_repository(self) -> None:
        """Adds all incoming withdrawals to recv_q"""

        for list_of_anns in self.recv_q.values():
            for ann in list_of_anns:
                self.rost_trusted_repository.add_ann(ann)

    def remove_anns_from_recv_q_that_should_be_withdrawn(self):
        for prefix, ann_list in self.recv_q.copy().items():
            new_ann_list = list()
            for ann in ann_list:
                # So long as it's not a new ann that has a suppressed withdrawal
                # add to recv_q
                if not (
                    ann.withdraw is False
                    and self.rost_trusted_repository.seen_withdrawal(ann)
                ):
                    new_ann_list.append(ann)
            self.recv_q[prefix] = new_ann_list

    def add_suppressed_withdrawals_back_to_recv_q(self, *args, **kwargs) -> None:
        for inner_dict in self.ribs_in.values():
            for ann_info in inner_dict.values():
                ribs_in_ann = ann_info.unprocessed_ann

                # Determine if the RIBsIn ann is already being withdrawn
                withdrawal_in_recv_q = False
                for ann in self.recv_q.get(ribs_in_ann.prefix, []):
                    if ribs_in_ann.as_path == ann.as_path:
                        withdrawal_in_recv_q = True

                # if ribs_in_ann withdrawal not in the recv_q,
                # and ribs_in_ann in the trusted repo, create a withdrawal
                if (
                    not withdrawal_in_recv_q
                    and self.rost_trusted_repository.seen_withdrawal(ribs_in_ann)
                ):
                    self.recv_q.add_ann(ribs_in_ann.copy({"withdraw": True}))
