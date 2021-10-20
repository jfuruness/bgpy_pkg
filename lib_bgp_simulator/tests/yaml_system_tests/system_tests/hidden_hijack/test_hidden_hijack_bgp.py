from pathlib import Path
import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ...utils import YamlSystemTestRunner

from .....enums import ASNs
from .....engine_input import SubprefixHijack
from .....engine import BGPAS
from .....engine import BGPRIBsAS


@pytest.mark.parametrize("BaseASCls", [BGPAS])#, BGPRIBsAS])
def test_hidden_hijack_bgp(BaseASCls):
    r"""Hidden hijack example with BGP
    Figure 1a in our ROV++ paper

        1
         \
         2 - 3
        /     \
       777     666
    """


    # Graph data
    peers = set([PeerLink(2, 3)])
    customer_providers = set([CPLink(provider_asn=1, customer_asn=2),
                              CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                              CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value)])
    # Number identifying the type of AS class
    as_classes = {asn: BaseASCls for asn in
                  list(range(1, 4)) + [ASNs.VICTIM.value, ASNs.ATTACKER.value]}

    empty_engine_kwargs = {"customer_provider_links": customer_providers,
                           "peer_links": peers,
                           "BaseASCls": BaseASCls}

    engine_input_kwargs = {"EngineInputCls": SubprefixHijack,
                           "attacker_asn": ASNs.ATTACKER.value,
                           "victim_asn": ASNs.VICTIM.value,
                           "as_classes": as_classes}

    dir_ = Path(__file__).parent

    # We need to split this dir up so that it can run over multiple BaseASCls
    dir_ = dir_ / BaseASCls.__name__
    dir_.mkdir(exist_ok=True)

    runner = YamlSystemTestRunner(dir_)

    runner.run_test(empty_engine_kwargs, engine_input_kwargs)
