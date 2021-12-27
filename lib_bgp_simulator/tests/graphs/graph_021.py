from lib_caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph021(GraphInfo):
    r"""
    Test withdrawal propagation with route leak from AS 666.

     777
     |  \
     \   2
      \ / \
       1   4
           |
           5

    The leak from AS 666 is path-poisoned with AS 4, so 4 should reject the new
    route as invalid but still propagate the withdrawal to 5. AS 5 should have
    no route in round 1.
    """

    def __init__(self):
        super(Graph021, self).__init__(
            peer_links=set([]),
            customer_provider_links=set(
                [CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=666),
                 CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=2),
                 CPLink(provider_asn=2, customer_asn=4),
                 CPLink(provider_asn=2, customer_asn=666),
                 CPLink(provider_asn=4, customer_asn=5),
                 ]))
