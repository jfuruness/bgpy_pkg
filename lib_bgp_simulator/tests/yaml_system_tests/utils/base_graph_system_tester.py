from pathlib import Path
import pytest



from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .yaml_system_test_runner import YamlSystemTestRunner

from ....enums import ASNs
from ....simulator import Scenario


class BaseGraphSystemTester:

    attacker_asn = ASNs.ATTACKER.value
    victim_asn = ASNs.VICTIM.value
    propagation_rounds = 1

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses"""

        super().__init_subclass__(*args, **kwargs)
        for attr in ["base_dir",
                     "GraphInfoCls",
                     "EngineInputCls"]:
            assert getattr(cls, attr, None) is not None, attr

    def test_graph(self):
        # Graph data
        peers = self.GraphInfoCls().peer_links
        customer_providers = self.GraphInfoCls().customer_provider_links

        empty_engine_kwargs = {"customer_provider_links": customer_providers,
                               "peer_links": peers,
                               "BaseASCls": self.BaseASCls}

        engine_input_kwargs = {"EngineInputCls": self.EngineInputCls,
                               "attacker_asn": self.attacker_asn,
                               "victim_asn": self.victim_asn,
                               "as_classes": self.as_classes}

        preloaded_engine = None
        preloaded_engine_input = None

        for propagation_round in range(self.propagation_rounds):
            # We need to split this dir up so that it can run over many BaseASCls
            dir_ = self.base_dir / self.BaseASCls.__name__
            dir_ = dir_ / self.propagation_round_str(propagation_round)
            dir_.mkdir(parents=True, exist_ok=True)

            runner = YamlSystemTestRunner(dir_,
                                          preloaded_engine=preloaded_engine,
                                          preloaded_engine_input=preloaded_engine_input)

            (preloaded_engine,
             preloaded_engine_input,
             scenario,
             traceback_guess) = runner.run_test(empty_engine_kwargs,
                                                 engine_input_kwargs)

        return preloaded_engine, preloaded_engine_input, traceback_guess

    def test_stable(self):
        preloaded_engine, preloaded_engine_input, preloaded_traceback_guess = self.test_graph()
        preloaded_engine_copy, _, __ = self.test_graph()

        scenario = Scenario(engine=preloaded_engine_copy, engine_input=preloaded_engine_input)
        subgraphs = {"all_ases": set([x.asn for x in preloaded_engine])}

        traceback_guess = scenario.run(subgraphs, 0)

        assert preloaded_engine == preloaded_engine_copy, "Unstable Graph"
        assert preloaded_traceback_guess == traceback_guess, "Unstable Graph"

    def propagation_round_str(self, propagation_round):
        return f"propogation_round_{propagation_round}"
