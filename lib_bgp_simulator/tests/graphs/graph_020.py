from lib_caida_collector import CustomerProviderLink as CPLink
from lib_caida_collector import PeerLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph020(GraphInfo):
    r"""
    Test basic withdrawals with route leak from AS 666.

   777  6
    |   |
    5=_ |
    |  \|
    |   4
     \ / \
     666--3

    Paths in ASes 3 and 4 should be changed in round 2. 6 will have no route in
    round 0, but it should receive the leaked route in round 1.
    """

    def __init__(self):
        super(Graph020, self).__init__(
            peer_links=set([PeerLink(666, 3)]),
            customer_provider_links=set(
                [CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=5),
                 CPLink(provider_asn=5, customer_asn=4),
                 CPLink(provider_asn=5, customer_asn=666),
                 CPLink(provider_asn=4, customer_asn=666),
                 CPLink(provider_asn=4, customer_asn=3),
                 CPLink(provider_asn=6, customer_asn=4),
                 ]))
