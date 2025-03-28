from ipaddress import ip_network
from pprint import pprint
from typing import TYPE_CHECKING

from frozendict import frozendict
from roa_checker import ROA

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.shared.enums import Outcomes, Plane, Prefixes, Relationships, Timestamps
from bgpy.simulation_engine import Announcement, ROV, SimulationEngine
from bgpy.simulation_framework import ASGraphAnalyzer, Scenario, ScenarioConfig

if TYPE_CHECKING:
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

announcements = list()

# announcements for 1.2.3.0/24
announcements.extend(
    [
        Announcement(
            # Prefix can be any valid prefix. By default it's 1.2.0.0/16
            prefix="1.2.3.0/24",
            # Where to forward the traffic on the data plane
            # When there is no path manipulation, set to the origin
            next_hop_asn=asn,
            # When there's no path manipulation, set to the origin
            as_path=(asn,),
            # Timestamps aren't used for anything yet but this is the default
            timestamp=(
                Timestamps.VICTIM.value if asn == 777 else Timestamps.ATTACKER.value
            ),
            # This is where you want the announcement to be seeded
            # Normally this is the origin, but in cases where there
            # is path manipulation and the origin is different, it can
            # be set to something else
            seed_asn=asn,
            # Indicates the announcement starts from the origin
            recv_relationship=Relationships.ORIGIN,
        )
        for asn in (777, 6, 8)
    ]
)
# announcements for 1.2.4.0/24
announcements.extend(
    [
        Announcement(
            prefix="1.2.4.0/24",
            next_hop_asn=asn,
            as_path=(asn,),
            timestamp=(
                Timestamps.VICTIM.value if asn == 88 else Timestamps.ATTACKER.value
            ),
            seed_asn=asn,
            recv_relationship=Relationships.ORIGIN,
        )
        for asn in (88, 10, 12)
    ]
)

scenario_config = ScenarioConfig(
    ScenarioCls=Scenario,
    num_victims=2,
    num_attackers=4,
    # Add ASes and their policies as necessary
    # hardcoded_asn_cls_dict=frozendict({}),
    # AdoptPolicyCls=ROV,
    override_attacker_asns=frozenset({6, 8, 10, 12}),
    override_victim_asns=frozenset({777, 88}),
    override_announcements=tuple(announcements),
    # Add as necessary (see previous example for how to make a ROA)
    # override_roas=tuple()
)

# Create the scenario
scenario = scenario_config.ScenarioCls(
    scenario_config=scenario_config,
    # No random adoption
    percent_adoption=0,
    engine=simulation_engine,
)

# Set up the engine. Set adopting ASes and seed announcements
simulation_engine.setup(scenario)

# Propagates announcements throughout the topology
simulation_engine.run(scenario=scenario)

# To get the local RIB at AS 1 for example
as_obj_12 = simulation_engine.as_graph.as_dict[12]
local_rib_12 = as_obj_12.policy.local_rib
print("AS 12 local RIB")
pprint(local_rib_12)

as_path = local_rib_12["1.2.3.0/24"].as_path
print(f"AS path of prefix 1.2.3.0/24: {as_path}")

# We can look at how the route propagated:
for asn in local_rib_12["1.2.3.0/24"].as_path:
    as_obj = simulation_engine.as_graph.as_dict[asn]
    print(f"Local RIB for {asn}, who is adopting {as_obj.policy.name}")
    pprint(as_obj.policy.local_rib)
