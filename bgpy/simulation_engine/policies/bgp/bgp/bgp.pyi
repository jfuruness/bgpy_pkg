from typing import Any

from _typeshed import Incomplete

from bgpy.as_graphs import AS as AS
from bgpy.shared.enums import Relationships as Relationships
from bgpy.shared.exceptions import GaoRexfordError as GaoRexfordError
from bgpy.simulation_engine.ann_containers import (
    LocalRIB as LocalRIB,
)
from bgpy.simulation_engine.ann_containers import (
    RecvQueue as RecvQueue,
)
from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.simulation_engine.policies.policy import Policy as Policy
from bgpy.simulation_framework import Scenario as Scenario

class BGP(Policy):
    name: str
    local_rib: Incomplete
    recv_q: Incomplete
    as_: Incomplete
    def __init__(
        self,
        local_rib: LocalRIB | None = None,
        recv_q: RecvQueue | None = None,
        as_: AS | None = None,
    ) -> None: ...
    def _get_best_ann_by_gao_rexford(
        self, current_ann: Ann | None, new_ann: Ann
    ) -> Ann: ...
    def _get_best_ann_by_local_pref(
        self, current_ann: Ann, new_ann: Ann
    ) -> Ann | None: ...
    def _get_best_ann_by_as_path(
        self, current_ann: Ann, new_ann: Ann
    ) -> Ann | None: ...
    def _get_best_ann_by_lowest_neighbor_asn_tiebreaker(
        self, current_ann: Ann, new_ann: Ann
    ) -> Ann: ...
    def seed_ann(self, ann: Ann) -> None: ...
    def receive_ann(self, ann: Ann, accept_withdrawals: bool = False) -> None: ...
    def process_incoming_anns(
        self,
        *,
        from_rel: Relationships,
        propagation_round: int,
        scenario: Scenario,
        reset_q: bool = True,
    ) -> None: ...
    def _valid_ann(self, ann: Ann, recv_relationship: Relationships) -> bool: ...
    def _copy_and_process(
        self,
        ann: Ann,
        recv_relationship: Relationships,
        overwrite_default_kwargs: dict[Any, Any] | None = None,
    ) -> Ann: ...
    def _reset_q(self, reset_q: bool) -> None: ...
    def propagate_to_providers(self) -> None: ...
    def propagate_to_customers(self) -> None: ...
    def propagate_to_peers(self) -> None: ...
    def _propagate(
        self, propagate_to: Relationships, send_rels: set[Relationships]
    ) -> None: ...
    def _policy_propagate(
        self,
        neighbor: AS,
        ann: Ann,
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool: ...
    def _prev_sent(self, neighbor: AS, ann: Ann) -> bool: ...
    def _process_outgoing_ann(
        self,
        neighbor: AS,
        ann: Ann,
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None: ...
    @property
    def _local_rib(self) -> LocalRIB: ...
    @property
    def _recv_q(self) -> RecvQueue: ...
    def __to_yaml_dict__(self) -> dict[Any, Any]: ...
    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Policy: ...
