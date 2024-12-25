from pathlib import Path

from frozendict import frozendict

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.shared.constants import SINGLE_DAY_CACHE_DIR
from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import ASPA, BGPiSec
from bgpy.simulation_framework import ScenarioConfig, Simulation, ShortestPathPrefixHijack


class DebugShortestPathExportAllPrefixHijack(ShortestPathPrefixHijack):
    """Attempting to determine why the paths are different for ASPA vs BGPiSec"""
    def _get_shortest_path_attacker_anns(self, *args, **kwargs) -> tuple["Ann", ...]:
        rv = super()._get_shortest_path_attacker_anns(*args, **kwargs)
        if self.scenario_config.AdoptPolicyCls == ASPA:
            [ann] = rv
            print(f"ASPA    : {ann.as_path}")
            print([asn in self.adopting_asns for asn in ann.as_path])
        return rv

    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        super().post_propagation_hook(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            propagation_round=propagation_round
        )
        if propagation_round == 0 and self.scenario_config.AdoptPolicyCls == BGPiSec:
            anns = [x for x in self.announcements if x.seed_asn in self.attacker_asns]
            [ann] = anns
            print(f"BGP-iSec: {ann.as_path}")
            print([asn in self.adopting_asns for asn in ann.as_path])
            print(ann.only_to_customers)
            # print(self.adopting_asns)


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        as_graph_constructor_kwargs=frozendict(
            {
                "as_graph_collector_kwargs": frozendict(
                    {
                        # dl_time: datetime(),
                        "cache_dir": SINGLE_DAY_CACHE_DIR,
                    }
                ),
                "as_graph_kwargs": frozendict(
                    {
                        # When no ASNs are stored, .9gb/core
                        # When one set of cones is stored, 1.6gb/core
                        # When both sets of cones are stored, 2.3gb/core
                        "store_customer_cone_size": True,
                        "store_customer_cone_asns": False,
                        "store_provider_cone_size": True,
                        "store_provider_cone_asns": True,
                    }
                ),
                "tsv_path": None,  # Path.home() / "Desktop" / "caida.tsv",
            }
        ),
        percent_adoptions=(0.99,),
        scenario_configs=tuple(
            [
                ScenarioConfig(
                    ScenarioCls=DebugShortestPathExportAllPrefixHijack,
                    AdoptPolicyCls=Cls
                )
                for Cls in [ASPA, BGPiSec]
            ]
        ),
        output_dir=Path("~/Desktop/spea_debug").expanduser(),
        num_trials=10,
        parse_cpus=1,
        python_hash_seed=0
    )
    sim.run()


if __name__ == "__main__":
    # bgp_dag = CAIDAASGraphConstructor(tsv_path=None).run()
    # print(bgp_dag.as_dict[58057].peer_asns)
    # ASPA    : (211909, 8781, 13335, 20473, 58057, 203718)
    # NOTE: here last is attacker, first is victim (which gets set to True)
    # Adopting:  False, False, True, True, True, False
    # BGP-iSec: (211909, 1101, 58057, 203718)
    # Adopting: False, False, True, False
    main()
