from pathlib import Path

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph010(GraphInfo):
    r"""
    TODO: Add pixel art
    """

    def __init__(self):
        super(Graph010, self).__init__(
            customer_provider_links=set([
                CPLink(provider_asn=1, customer_asn=3),
                CPLink(provider_asn=1, customer_asn=2),
                CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=2, customer_asn=4),
                CPLink(provider_asn=2, customer_asn=5)
            ])
        )
