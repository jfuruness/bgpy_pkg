from typing import Optional, TYPE_CHECKING

from .propagate_funcs import _propagate
from .propagate_funcs import _process_outgoing_ann
from .propagate_funcs import _prev_sent
from .propagate_funcs import _send_anns

from .process_incoming_funcs import process_incoming_anns
from .process_incoming_funcs import _new_ann_better
from .process_incoming_funcs import _process_incoming_withdrawal
from .process_incoming_funcs import _withdraw_ann_from_neighbors
from .process_incoming_funcs import _select_best_ribs_in

from bgpy.simulation_engine.policies.bgp import BGP

from bgpy.simulation_engine.ann_containers import RIBsIn
from bgpy.simulation_engine.ann_containers import RIBsOut
from bgpy.simulation_engine.ann_containers import SendQueue


if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPFull(BGP):
    name = "BGP Full"

    def __init__(
        self,
        *args,
        _ribs_in: Optional[RIBsIn] = None,
        _ribs_out: Optional[RIBsOut] = None,
        _send_q: Optional[SendQueue] = None,
        **kwargs,
    ):
        super(BGPFull, self).__init__(*args, **kwargs)
        self._ribs_in: RIBsIn = _ribs_in if _ribs_in else RIBsIn()
        self._ribs_out: RIBsOut = _ribs_out if _ribs_out else RIBsOut()
        self._send_q: SendQueue = _send_q if _send_q else SendQueue()

    # Propagation functions
    _propagate = _propagate
    _process_outgoing_ann = _process_outgoing_ann
    _prev_sent = _prev_sent  # type: ignore
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
    process_incoming_anns = process_incoming_anns
    _new_ann_better = _new_ann_better
    _process_incoming_withdrawal = _process_incoming_withdrawal
    _withdraw_ann_from_neighbors = _withdraw_ann_from_neighbors
    _select_best_ribs_in = _select_best_ribs_in

    # Must be here since it referes to BGPFull
    # Could just use super but want to avoid the additional func calls
    def receive_ann(  # type: ignore
        self, ann: "Ann", accept_withdrawals: bool = True
    ) -> None:
        BGP.receive_ann(self, ann, accept_withdrawals=True)

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPFull, self).__to_yaml_dict__()
        as_dict.update(
            {
                "_ribs_in": self._ribs_in,
                "_ribs_out": self._ribs_out,
                "_send_q": self._send_q,
            }
        )
        return as_dict
