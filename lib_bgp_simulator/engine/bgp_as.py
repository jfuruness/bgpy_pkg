from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .incoming_anns import IncomingAnns
from .bgp_policy import BGPPolicy
from ..relationships import Relationships
from ..announcement import Announcement as Ann


class BGPAS(AS):
    __slots__ = ["local_rib", "incoming_anns", "policy"]

    def __init__(self, *args, **kwargs):
        super(BGPAS, self).__init__(*args, **kwargs)
        self.policy = BGPPolicy()
        # Dicts were just .25s slower, but this way
        # Will make it very easy to do traceback
        self.local_rib = LocalRib()
        self.incoming_anns = IncomingAnns()

    def propagate_to_providers(self):
        """Propogates to providers"""

        self.policy.propagate_to_providers(self)

    def propagate_to_customers(self):
        """Propogates to customers"""

        self.policy.propagate_to_customers(self)

    def propagate_to_peers(self):
        """Propogates to peers"""

        self.policy.propagate_to_peers(self)

    def process_incoming_anns(self, recv_relationship: Relationships):
        """Process all announcements that were incoming from a specific rel"""

        self.policy.process_incoming_anns(self, recv_relationship)
