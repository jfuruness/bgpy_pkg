"""Example showing:

* hardcoded_asn_cls_dict - how to force some ASes to always adopt
* scenario_label - how to customize your labels
* CAIDAASGraphConstructor - How to build the BGP dag independent of the simulations

Runs a simulation comparing a subprefix hijack with ROV adopted randomly
vs ROV always adopted at the top, and elsewhere adopted randomly.

Additionally, just for the purposes of this example, make the attacker a transit
AS that is not a tier-1 AS
"""

from pathlib import Path

from frozendict import frozendict

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.shared.enums import ASGroups, SpecialPercentAdoptions
from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import (
    ScenarioConfig,
    Simulation,
    SubprefixHijack,
)


def main():
    # Get the tier-1 ASes
    bgp_dag = CAIDAASGraphConstructor(tsv_path=None).run()
    # NOTE: if you wanted to get the ASes instead of ASNs, use as_groups
    input_clique_asns = bgp_dag.asn_groups[ASGroups.INPUT_CLIQUE.value]
    hardcoded_asn_cls_dict = frozendict({asn: ROV for asn in input_clique_asns})

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            0.99,
            # Using only 1 AS not adopting causes extreme variance
            # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=ROV,
                scenario_label="ROV w/random adoption",
                # Make the attacker a transit AS that is not a tier-1 AS for ex purposes
                attacker_subcategory_attr=ASGroups.ETC.value,
            ),
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=ROV,
                hardcoded_asn_cls_dict=hardcoded_asn_cls_dict,
                scenario_label="ROV w/tier1 always adopting",
                # Each of these categories adopt randomly using percent_adoptions
                adoption_subcategory_attrs=(
                    ASGroups.STUBS_OR_MH.value,
                    ASGroups.ETC.value,
                    # This is normally included in the default, but since
                    # in this example tier-1 ASes always adopt, omit this
                    # ASGroups.INPUT_CLIQUE.value,
                ),
                # Make the attacker a transit AS that is not a tier-1 AS for ex purposes
                attacker_subcategory_attr=ASGroups.ETC.value,
            ),
        ),
        output_dir=Path("~/Desktop/scenario_config_examples").expanduser(),
        num_trials=1,
        parse_cpus=1,
    )
    sim.run()


if __name__ == "__main__":
    main()
