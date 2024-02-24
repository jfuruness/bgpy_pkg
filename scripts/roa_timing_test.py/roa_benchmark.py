from pathlib import Path
from time import perf_counter

from bgpy.enums import Prefixes, Relationships, Timestamps
from bgpy.simulation_engine import BGP

from bgpy.simulation_framework import (
    Simulation,
    ScenarioConfig,
    SubprefixHijack,
)
from bgpy.simulation_framework.scenarios.roa_info import ROAInfo


def _get_announcements(self, *args, **kwargs):
    anns = list()
    for victim_asn in self.victim_asns:
        anns.append(
            self.scenario_config.AnnCls(
                prefix=Prefixes.PREFIX.value,
                next_hop_asn=victim_asn,
                as_path=(victim_asn,),
                timestamp=Timestamps.VICTIM.value,
                seed_asn=victim_asn,
                roa_valid_length=True,
                roa_origin=victim_asn,
                recv_relationship=Relationships.ORIGIN,
            )
        )

    err: str = "Fix the roa_origins of the " "announcements for multiple victims"
    assert len(self.victim_asns) == 1, err

    roa_origin: int = next(iter(self.victim_asns))

    for attacker_asn in self.attacker_asns:
        anns.append(
            self.scenario_config.AnnCls(
                prefix=Prefixes.SUBPREFIX.value,
                next_hop_asn=attacker_asn,
                as_path=(attacker_asn,),
                timestamp=Timestamps.ATTACKER.value,
                seed_asn=attacker_asn,
                roa_valid_length=False,
                roa_origin=roa_origin,
                recv_relationship=Relationships.ORIGIN,
            )
        )
    return tuple(anns)


class SubprefixHijackWOutROAs(SubprefixHijack):
    def _get_roa_infos(*args, **kwargs):
        return ()
    _get_announcements = _get_announcements


class SubprefixHijackWROAs(SubprefixHijack):
    def _get_roa_infos(self, *args, **kwargs):
        assert len(self.victim_asns) == 1
        roa_origin: int = next(iter(self.victim_asns))
        return tuple(
            [
                ROAInfo(
                    prefix=Prefixes.PREFIX.value,
                    origin=roa_origin,
                )
            ]
        )

    _get_announcements = _get_announcements


def main():
    """Runs the defaults"""

    assert False, "Run with pypy3 -O"

    benchmark_sim_kwargs = {
        "percent_adoptions": (.1, .5, .8),
        "output_dir": Path.home() / "Desktop" / "roa_benchmarks",
        "num_trials": 100,
        "parse_cpus": 1,
        "python_hash_seed": 0,
    }

    sim = Simulation(
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijackWOutROAs,
                AdoptPolicyCls=BGP,
            ),
        ),
        **benchmark_sim_kwargs
    )
    start = perf_counter()
    sim.run(GraphFactoryCls=None)
    print(perf_counter() - start)

    ############################
    # Optimized implementation #
    ############################

    sim = Simulation(
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijackWROAs,
                AdoptPolicyCls=BGP,
            ),
        ),
        **benchmark_sim_kwargs,
    )
    start = perf_counter()
    sim.run(GraphFactoryCls=None)
    print(perf_counter() - start)


if __name__ == "__main__":
    main()
