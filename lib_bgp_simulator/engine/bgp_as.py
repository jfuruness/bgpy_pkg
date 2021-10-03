from copy import deepcopy

from lib_caida_collector import AS

from .bgp_policy import BGPPolicy
from ..enums import Relationships
from ..announcement import Announcement as Ann


class BGPAS(AS):
    __slots__ = ["policy"]

    def __init__(self, *args, **kwargs):
        super(BGPAS, self).__init__(*args, **kwargs)
        self.policy = BGPPolicy()

    def propagate_to_providers(self):
        """Propogates to providers"""

        self.policy.propagate_to_providers(self)

    def propagate_to_customers(self):
        """Propogates to customers"""

        self.policy.propagate_to_customers(self)

    def propagate_to_peers(self):
        """Propogates to peers"""

        self.policy.propagate_to_peers(self)

    def process_incoming_anns(self, recv_relationship: Relationships, *args, **kwargs):
        """Process all announcements that were incoming from a specific rel"""

        self.policy.process_incoming_anns(self, recv_relationship, *args, **kwargs)
