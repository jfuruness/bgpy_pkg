class GraphInfo:
    """Contains information to build a graph"""

    def __init__(self, customer_provider_links=None, peer_links=None):
        if customer_provider_links:
            self.customer_provider_links = customer_provider_links
        else:
            self.customer_provider_links = set()

        self.peer_links = peer_links if peer_links else set()
