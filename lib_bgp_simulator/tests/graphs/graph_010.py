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
                CPLink(provider_asn=88, customer_asn=33)
                CPLink(provider_asn=88, customer_asn=86),
                CPLink(provider_asn=88, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=33, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=86, customer_asn=22),
                CPLink(provider_asn=86, customer_asn=11)
            ])
        )
