from pathlib import Path

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph004(GraphInfo):
    r"""v2 example with ROV++V1 and ROV

              /44\
             / / \\attacker_asn
            /  54 \ 
           /  /    56
          77  55    \
           | /       victim_asn
          11    
          / \
         32 33  
        """

    def __init__(self):
        super(Graph004, self).__init__(
            customer_provider_links=set(
                [CPLink(provider_asn=44, customer_asn=77),
                 CPLink(provider_asn=44, customer_asn=54),
                 CPLink(provider_asn=44, customer_asn=56),
                 CPLink(provider_asn=44, customer_asn=ASNs.ATTACKER.value),
                 CPLink(provider_asn=77, customer_asn=11),
                 CPLink(provider_asn=11, customer_asn=32),
                 CPLink(provider_asn=11, customer_asn=33),
                 CPLink(provider_asn=54, customer_asn=55),
                 CPLink(provider_asn=55, customer_asn=11),
                 CPLink(provider_asn=56, customer_asn=ASNs.VICTIM.value)]))
