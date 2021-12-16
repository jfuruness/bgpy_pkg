from pathlib import Path

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph016(GraphInfo):
    r"""
    TODO: Add reference to image online (it's a bit much for pixel art)
    Mini internet test topology with attacker directly connected to 14.
    """
    def __init__(self):
        super(Graph016, self).__init__(
            peer_links=set([
                PeerLink(1, 2),
                PeerLink(2, 4),
                PeerLink(4, 3),
                PeerLink(3, 1),
                PeerLink(2, 3),
                PeerLink(1, 4),
                PeerLink(5, 2),
                PeerLink(5, 11),
                PeerLink(13, 12),
                PeerLink(12, 6),
                PeerLink(6, 7),
                PeerLink(14, 8),
                PeerLink(8, 9),
                PeerLink(9, 10)
            ]),
            customer_provider_links=set([
                CPLink(provider_asn=11, customer_asn=12),
                CPLink(provider_asn=11, customer_asn=13),
                CPLink(provider_asn=5, customer_asn=6),
                CPLink(provider_asn=5, customer_asn=12),
                CPLink(provider_asn=2, customer_asn=12),
                CPLink(provider_asn=2, customer_asn=6),
                CPLink(provider_asn=2, customer_asn=7),
                CPLink(provider_asn=13, customer_asn=14),
                CPLink(provider_asn=12, customer_asn=14),
                CPLink(provider_asn=6, customer_asn=8),
                CPLink(provider_asn=6, customer_asn=9),
                CPLink(provider_asn=7, customer_asn=9),
                CPLink(provider_asn=7, customer_asn=10),
                CPLink(provider_asn=14, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=14, customer_asn=21),
                CPLink(provider_asn=14, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=14, customer_asn=19),
                CPLink(provider_asn=8, customer_asn=19),
                CPLink(provider_asn=9, customer_asn=19),
                CPLink(provider_asn=9, customer_asn=18),
                CPLink(provider_asn=9, customer_asn=16),
                CPLink(provider_asn=9, customer_asn=15),
                CPLink(provider_asn=10, customer_asn=17),
                CPLink(provider_asn=10, customer_asn=15),
                CPLink(provider_asn=1, customer_asn=23),
                CPLink(provider_asn=3, customer_asn=23),
                CPLink(provider_asn=4, customer_asn=23),
                CPLink(provider_asn=23, customer_asn=24),
                CPLink(provider_asn=24, customer_asn=25)
            ])
    )

# NOTE: This code below provides partial functionality needed 
# to allow the assignment of attacker and victim as class argument.
# This is not complete in this class. Maybe a feature for future.
#
#        # Assign attaker
#        self._replace_as(attacker_as, ASNs.ATTACKER.value)
#        # Assign victim
#        self._replace_as(victim_as, ASNs.VICTIM.value)
#        # Create relationship link objects
#        customer_provider_links = [CPLink(provider_asn=x[0], customer_asn=x[1]) for x in provider_customer_rows]
#        peer_links = [PeerLink(x[0], x[1]) for x in peer_rows]
#
#        def _replace_as(as_to_replace, replacement_as, rows):
#            """
#            Given the rows (i.e. a list of lists which define the relationships)
#            replace `as_to_replace` with the `replacement_as`.
#            """
#            for row in rows:
#                row = [replacement_as if x == as_to_replace else x for x in row]
#
