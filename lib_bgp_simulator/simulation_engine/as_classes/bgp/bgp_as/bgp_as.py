from typing import List, Optional

from ..bgp_simple_as import BGPSimpleAS

from ....ann_containers import RIBsIn
from ....ann_containers import RIBsOut
from ....ann_containers import SendQueue

from ....announcement import Announcement as Ann
from .....enums import Relationships


class BGPAS(BGPSimpleAS):
    __slots__ = tuple()  # type: ignore

    name = "BGP"

    def __init__(self,
                 *args,
                 _ribs_in: Optional[RIBsIn] = None,
                 _ribs_out: Optional[RIBsOut] = None,
                 _send_q: Optional[SendQueue] = None,
                 **kwargs):
        super(BGPAS, self).__init__(*args, **kwargs)
        self._ribs_in = _ribs_in if _ribs_in else RIBsIn()
        self._ribs_out = _ribs_out if _ribs_out else RIBsOut()
        self._send_q = _send_q if _send_q else SendQueue()

    # Propagation functions
    from .propagate_funcs import _propagate  # type: ignore
    from .propagate_funcs import _process_outgoing_ann  # type: ignore
    from .propagate_funcs import _prev_sent  # type: ignore
    from .propagate_funcs import _send_anns  # type: ignore

    # Must add this func here since it refers to BGPAS
    # Could use super but want to avoid additional func calls
    def _populate_send_q(self,
                         propagate_to: Relationships,
                         send_rels: List[Relationships]) -> None:
        # Process outging ann is oerriden so this just adds to send q
        super(BGPAS, self)._propagate(propagate_to, send_rels)

    # Process incoming funcs
    from .process_incoming_funcs import process_incoming_anns  # type: ignore
    from .process_incoming_funcs import \
        _process_incoming_withdrawal  # type: ignore
    from .process_incoming_funcs import \
        _withdraw_ann_from_neighbors  # type: ignore
    from .process_incoming_funcs import _select_best_ribs_in  # type: ignore

    # Must be here since it referes to BGPAS
    # Could just use super but want to avoid the additional func calls
    def receive_ann(self, ann: Ann) -> None:
        super(BGPAS, self).receive_ann(ann, accept_withdrawals=True)

    def __to_yaml_dict__(self) -> dict:
        """This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPAS, self).__to_yaml_dict__()
        as_dict.update({"_ribs_in": self._ribs_in,
                        "_ribs_out": self._ribs_out,
                        "_send_q": self._send_q})
        return as_dict
