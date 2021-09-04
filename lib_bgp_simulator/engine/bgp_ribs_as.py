from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .bgp_as import BGPAS
from .ribs import RibsIn, RibsOut
from .ann_queues import SendQueue, RecvQueue
from .relationships import Relationships
from ..announcement import Announcement as Ann
from .bgp_ribs_policy import BGPRIBSPolicy


class BGPRIBSAS(BGPAS):
    __slots__ = ["local_rib", "incoming_anns", "policy", 
        "ribs_in", "ribs_out", "recv_q", "send_q"]

    def __init__(self, *args, **kwargs):
        super(BGPRIBSAS, self).__init__(*args, **kwargs)
        #self.incoming_anns = IncomingAnns()
        #self.local_rib = LocalRib()
        self.ribs_in = RibsIn()
        self.ribs_out = RibsOut()
        self.recv_q = RecvQueue()
        self.send_q = SendQueue()
        self.policy = BGPRIBSPolicy()

