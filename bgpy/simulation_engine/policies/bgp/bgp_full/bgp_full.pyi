from _typeshed import Incomplete

from bgpy.shared.enums import Relationships as Relationships
from bgpy.simulation_engine.ann_containers import (
    AnnInfo as AnnInfo,
)
from bgpy.simulation_engine.ann_containers import (
    RIBsIn as RIBsIn,
)
from bgpy.simulation_engine.ann_containers import (
    RIBsOut as RIBsOut,
)
from bgpy.simulation_engine.ann_containers import (
    SendInfo as SendInfo,
)
from bgpy.simulation_engine.ann_containers import (
    SendQueue as SendQueue,
)
from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.simulation_engine.policies.bgp import BGP as BGP
from bgpy.simulation_framework import Scenario as Scenario

class BGPFull(BGP):
    name: str
    ribs_in: Incomplete
    ribs_out: Incomplete
    send_q: Incomplete
    def __init__(
        self,
        *args,
        ribs_in: RIBsIn | None = None,
        ribs_out: RIBsOut | None = None,
        send_q: SendQueue | None = None,
        **kwargs,
    ) -> None: ...
    @property
    def _ribs_in(self) -> RIBsIn: ...
    @property
    def _ribs_out(self) -> RIBsOut: ...
    @property
    def _send_q(self) -> SendQueue: ...
    def process_incoming_anns(
        self,
        *,
        from_rel: Relationships,
        propagation_round: int,
        scenario: Scenario,
        reset_q: bool = True,
    ): ...
    def _new_ann_better(
        self,
        current_ann: Ann | None,
        current_processed: bool,
        default_current_recv_rel: Relationships,
        new_ann: Ann | None,
        new_processed: bool,
        default_new_recv_rel: Relationships,
    ) -> bool: ...
    def _process_incoming_withdrawal(
        self, ann: Ann, recv_relationship: Relationships
    ) -> bool: ...
    def _withdraw_ann_from_neighbors(self, withdraw_ann: Ann) -> None: ...
    def _select_best_ribs_in(self, prefix: str) -> Ann | None: ...
    def _populate_send_q(
        self, propagate_to: Relationships, send_rels: set[Relationships]
    ) -> None: ...
    def receive_ann(self, ann: Ann, accept_withdrawals: bool = True) -> None: ...
    def __to_yaml_dict__(self): ...
