from lib_caida_collector import CustomerProviderLink as CPLink
from lib_caida_collector import PeerLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph022(GraphInfo):
    r"""
    Test next-best announcement selection after a withdrawal using a route leak
    from AS 666.

     777---1
     |  \  |
     \   2 3
      \ / \|
      666  4
           |
           5

    The leak from AS 666 is path-poisoned with AS 4, so 4 will reject the new
    route as invalid. This test verifies that 4 correctly chooses the longer,
    but still valid path from AS 3.
    """

    def __init__(self):
        super(Graph022, self).__init__(
            peer_links=set([PeerLink(ASNs.VICTIM.value, 1)]),
            customer_provider_links=set(
                [CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=666),
                 CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=2),
                 CPLink(provider_asn=2, customer_asn=4),
                 CPLink(provider_asn=2, customer_asn=666),
                 CPLink(provider_asn=4, customer_asn=5),
                 CPLink(provider_asn=1, customer_asn=3),
                 CPLink(provider_asn=3, customer_asn=4),
                 ]))
