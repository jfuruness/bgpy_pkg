from pathlib import Path

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph011(GraphInfo):
    r"""
    TODO: Add reference to image online (it's a bit much for pixel art)
    """
    def __init__(self):
        super(Graph011, self).__init__(
            peer_links=set([
                PeerLink(24875, 52320),
                PeerLink(52320, 12389)
            ]),
            customer_provider_links=set([
                CPLink(provider_asn=174,customer_asn=213371),
                CPLink(provider_asn=174,customer_asn=31133),
                CPLink(provider_asn=213371,customer_asn=208673),
                CPLink(provider_asn=31133,customer_asn=1299),
                CPLink(provider_asn=1299,customer_asn=12389),
                CPLink(provider_asn=2914,customer_asn=24875),
                CPLink(provider_asn=24875,customer_asn=213371),
                CPLink(provider_asn=52320,customer_asn=53180),
                CPLink(provider_asn=53180,customer_asn=268337),
                CPLink(provider_asn=268337,customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=12389,customer_asn=ASNs.ATTACKER.value)
            ])
    )
