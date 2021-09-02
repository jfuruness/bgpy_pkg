from lib_caida_collector import AS

from .bgp_policy import BGPPolicy


class BGPAS(AS):
    __slots__ = ["policy"]

    def __init__(self, *args, **kwargs):
        super(BGPAS, self).__init__(*args, **kwargs)
        self.policy = BGPPolicy

    def propagate_to_providers(self):
        """Propogates to providers"""

        self.policy.propagate_to_providers()

    def propagate_to_customers(self):
        """Propogates to customers"""

        self.policy.propagate_to_customers()

    def propagate_to_peers(self):
        """Propogates to peers"""

        self.policy.propagate_to_peers()

    def process_incoming_anns(self, *args, **kwargs):
        """Process all announcements that were incoming from a specific rel"""

        self.policy.process_incoming_anns(*args, **kwargs)
