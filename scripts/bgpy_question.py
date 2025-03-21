from ipaddress import ip_network
from pprint import pprint
from typing import TYPE_CHECKING

from frozendict import frozendict
from roa_checker import ROA

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.shared.enums import Outcomes, Plane, Prefixes, Relationships, Timestamps
from bgpy.simulation_engine import ROV, SimulationEngine
from bgpy.simulation_framework import ASGraphAnalyzer, Scenario, ScenarioConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine

# Creating the BGP Dag/AS topology
# Storing customer and/or provider cones takes up way more memory
caida_as_graph = CAIDAASGraphConstructor(
    as_graph_kwargs=frozendict(
        {
            "store_customer_cone_size": True,
            "store_customer_cone_asns": False,
            "store_provider_cone_size": False,
            "store_provider_cone_asns": False,
        }
    )
).run()
# Engine that runs the propagation
simulation_engine = SimulationEngine(caida_as_graph)

# If you just want to play around with the AS Graph, you can access it here:
as_graph = simulation_engine.as_graph

# Example of how to access a specific AS
as_obj = as_graph.as_dict[6]
# Get all customers of the AS
customer_as_objects = as_obj.customers
# Get all the customer ASNs of the AS
customer_asns = as_obj.customer_asns


class CustomScenario(Scenario):
    def _get_announcements(
        self,
        *,
        engine: "BaseSimulationEngine | None" = None,
    ) -> tuple["Ann", ...]:
        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    # Prefix can be any valid prefix. By default it's 1.2.0.0/16
                    prefix=Prefixes.PREFIX.value,
                    # Where to forward the traffic on the data plane
                    # When there is no path manipulation, set to the origin
                    next_hop_asn=victim_asn,
                    # When there's no path manipulation, set to the origin
                    as_path=(victim_asn,),
                    # Timestamps aren't used for anything yet but this is the default
                    timestamp=Timestamps.VICTIM.value,
                    # This is where you want the announcement to be seeded
                    # Normally this is the origin, but in cases where there
                    # is path manipulation and the origin is different, it can
                    # be set to something else
                    seed_asn=victim_asn,
                    # Indicates the announcement starts from the origin
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        return tuple(anns)

    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: "BaseSimulationEngine | None" = None,
    ) -> tuple[ROA, ...]:
        """Returns a tuple of ROAs"""

        return tuple(
            [
                ROA(
                    prefix=ip_network(Prefixes.PREFIX.value),
                    origin=x,
                    # By default, max length is equal to prefix length
                    # max_length="16"
                )
                for x in self.victim_asns
            ]
        )


# Create the ScenarioConfig
attackers = frozenset({6, 8})
scenario_config = ScenarioConfig(
    ScenarioCls=CustomScenario,
    num_victims=1,
    num_attackers=len(attackers),
    hardcoded_asn_cls_dict=frozendict(
        {
            1: ROV,
            2: ROV,
            777: ROV,
        }
    ),
    AdoptPolicyCls=ROV,
    override_attacker_asns=attackers,
    override_victim_asns=frozenset({777}),
    # Alternatively, instead of defining a Scenario every time,
    # you can just use override_announcements and override_roas
    # attribute if you are just looking to run your scenario
    # a single time
)

# Create the scenario
scenario = scenario_config.ScenarioCls(
    scenario_config=scenario_config,
    # Percent of random adoption of scenario_config.AdoptPolicyCls
    # which in this case is ROV
    # Since you want to decide these ASes for yourself,
    # you can set this to 0 and hardocde them in the
    # scenario_config.hardcoded_asn_cls_dict
    percent_adoption=0,  # ex: .5 for 50% random adoption
    engine=simulation_engine,
)

# Set up the engine. Set adopting ASes and seed announcements
simulation_engine.setup(scenario)

# Propagates announcements throughout the topology
simulation_engine.run(scenario=scenario)

# To get the local RIB at AS 1 for example
as_obj_1 = simulation_engine.as_graph.as_dict[1]
local_rib_1 = as_obj_1.policy.local_rib
print("AS 1 local RIB")
pprint(local_rib_1)

# To get where each AS traces back to on the data plane:
as_graph_analyzer = ASGraphAnalyzer(simulation_engine, scenario)
outcomes = as_graph_analyzer.analyze()
data_plane_outcomes = outcomes[Plane.DATA.value]
# See what the outcome was for AS 1 for the most specific prefix
as_1_outcome = data_plane_outcomes[1]
# Convert as_1_outcome integer to a readable name using the enum
as_1_outcome_name = Outcomes(as_1_outcome).name
print(f"{as_1_outcome_name=}")
