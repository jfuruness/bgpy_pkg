from typing import TYPE_CHECKING
from warnings import warn

from bgpy.simulation_engine.ann_containers import RIBsIn, RIBsOut, SendQueue
from bgpy.simulation_engine.policies.bgp import BGP

from .process_incoming_funcs import (
    _new_ann_better,
    _process_incoming_withdrawal,
    _select_best_ribs_in,
    _withdraw_ann_from_neighbors,
    process_incoming_anns,
)
from .propagate_funcs import _prev_sent, _process_outgoing_ann, _propagate, _send_anns

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPFull(BGP):
    name = "BGP Full"

    def __init__(
        self,
        *args,
        ribs_in: RIBsIn | None = None,
        ribs_out: RIBsOut | None = None,
        send_q: SendQueue | None = None,
        **kwargs,
    ):
        super(BGPFull, self).__init__(*args, **kwargs)
        self.ribs_in: RIBsIn = ribs_in if ribs_in else RIBsIn()
        self.ribs_out: RIBsOut = ribs_out if ribs_out else RIBsOut()
        self.send_q: SendQueue = send_q if send_q else SendQueue()

    @property
    def _ribs_in(self) -> RIBsIn:
        warn(
            "Please use .ribs_in instead of ._ribs_in. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.ribs_in

    @property
    def _ribs_out(self) -> RIBsOut:
        warn(
            "Please use .ribs_out instead of ._ribs_out. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.ribs_out

    @property
    def _send_q(self) -> SendQueue:
        warn(
            "Please use .send_q instead of ._send_q. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.send_q

    # Propagation functions
    _propagate = _propagate
    _process_outgoing_ann = _process_outgoing_ann
    _prev_sent = _prev_sent
    _send_anns = _send_anns

    # Must add this func here since it refers to BGPFull
    # Could use super but want to avoid additional func calls
    def _populate_send_q(
        self,
        propagate_to: "Relationships",
        send_rels: set["Relationships"],
    ) -> None:
        # Process outging ann is oerriden so this just adds to send q
        super(BGPFull, self)._propagate(propagate_to, send_rels)

    # Process incoming funcs
    if not TYPE_CHECKING:
        process_incoming_anns = process_incoming_anns
        _new_ann_better = _new_ann_better
        _process_incoming_withdrawal = _process_incoming_withdrawal
        _withdraw_ann_from_neighbors = _withdraw_ann_from_neighbors
        _select_best_ribs_in = _select_best_ribs_in

    # NOTE: not sure why this is coded in such a weird fashion...
    def receive_ann(self, ann: "Ann", accept_withdrawals: bool = True) -> None:
        BGP.receive_ann(self, ann, accept_withdrawals=True)

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPFull, self).__to_yaml_dict__()
        as_dict.update(
            {
                "ribs_in": self.ribs_in,
                "ribs_out": self.ribs_out,
                "send_q": self.send_q,
            }
        )
        return as_dict
