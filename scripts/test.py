import time

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.enums import PyRelationships as Relationships
from bgpy.enums import CPPRelationships
from bgpy.simulation_engines.py_simulation_engine import (
    PySimulationEngine,
    PyAnnouncement as PyAnn,
)
from bgpy.simulation_engines.cpp_simulation_engine import (
    CPPSimulationEngine,
    CPPAnnouncement as CPPAnn,
)

from typing import Any, Optional, TYPE_CHECKING, Union

from frozendict import frozendict

from bgpy.enums import PyRelationships
from bgpy.simulation_engines.base import SimulationEngine
from bgpy.simulation_engines.base import Policy
from bgpy.simulation_engines.py_simulation_engine.policies import BGPSimplePolicy

# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn
    from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn
    from bgpy.simulation_framework import Scenario


class ExrPySimulationEngine(SimulationEngine):
    """Python simulation engine representation"""

    ###############
    # Setup funcs #
    ###############

    def setup(
        self,
        announcements: tuple[Union["PyAnn", "CPPAnn"], ...] = (),
        BasePolicyCls: type[Policy] = BGPSimplePolicy,
        non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            frozendict()  # type: ignore
        ),
        prev_scenario: Optional["Scenario"] = None,
    ) -> frozenset[type[Policy]]:
        """Sets AS classes and seeds announcements"""

        policies_used: frozenset[type[Policy]] = self._set_as_classes(
            BasePolicyCls, non_default_asn_cls_dict, prev_scenario
        )
        self._seed_announcements(announcements, prev_scenario)
        self.ready_to_run_round = 0
        return policies_used

    def _set_as_classes(
        self,
        BasePolicyCls: type[Policy],
        non_default_asn_cls_dict: frozendict[int, type[Policy]],
        prev_scenario: Optional["Scenario"] = None,
    ) -> frozenset[type[Policy]]:
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        policy_classes_used = set()
        # Done here to save as much time  as possible
        for as_obj in self.as_graph:
            # Delete the old policy and remove references so that RAM can be reclaimed
            del as_obj.policy.as_
            # set the AS class to be the proper type of AS
            Cls = non_default_asn_cls_dict.get(as_obj.asn, BasePolicyCls)
            as_obj.policy = Cls(as_=as_obj)
            policy_classes_used.add(Cls)
        return frozenset(policy_classes_used)

    def _seed_announcements(
        self,
        announcements: tuple[Union["PyAnn", "CPPAnn"], ...] = (),
        prev_scenario: Optional["Scenario"] = None,
    ) -> None:
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        print("This will break when seeding along the path. Pass dict of seed_asn: ann instead")
        for ann in announcements:
            seed_asn = getattr(ann, "seed_asn", ann.as_path[-1])
            # Get the AS object to seed at
            # Must ignore type because it doesn't see assert above
            obj_to_seed = self.as_graph.as_dict[seed_asn]  # type: ignore
            # Ensure we aren't replacing anything
            err = "Seeding conflict"
            assert obj_to_seed.policy._local_rib.get_ann(ann.prefix) is None, err
            # Seed by placing in the local rib
            obj_to_seed.policy._local_rib.add_ann(ann)

    #####################
    # Propagation funcs #
    #####################

    def run(self, propagation_round: int = 0, scenario: Optional["Scenario"] = None):
        """Propogates announcements and ensures proper setup"""

        # Ensure that the simulator is ready to run this round
        if self.ready_to_run_round != propagation_round:
            raise Exception(f"Engine not set up to run for {propagation_round} round")
        assert scenario, "This can't be empty"

        # import time
        # start = time.perf_counter()
        # Propogate anns
        self._propagate(propagation_round, scenario)
        # print(f"prop time {time.perf_counter() - start}")
        # Increment the ready to run round
        self.ready_to_run_round += 1

    def _propagate(self, propagation_round: int, scenario: "Scenario"):
        """Propogates announcements

        to stick with Gao Rexford, we propagate to
        0. providers
        2. peers
        3. customers
        """

        self._propagate_to_providers(propagation_round, scenario)
        self._propagate_to_peers(propagation_round, scenario)
        self._propagate_to_customers(propagation_round, scenario)

    def _propagate_to_providers(self, propagation_round: int, scenario: "Scenario", valid_propagate_up):
        """Propogate to providers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        for i, rank in enumerate(self.as_graph.propagation_ranks):
            # Nothing to process at the start
            if i > 0:
                # Process first because maybe it recv from lower ranks
                for as_obj in rank:
                    if as_obj.asn in valid_propagate_up:
                        as_obj.policy.process_incoming_anns(
                            from_rel=PyRelationships.CUSTOMERS,
                            propagation_round=propagation_round,
                            scenario=scenario,
                        )
            # Send to the higher ranks
            for as_obj in rank:
                if as_obj.asn in valid_propagate_up:
                    as_obj.policy.propagate_to_providers()

    def _propagate_to_peers(
        self, propagation_round: int, scenario: Optional["Scenario"], valid_propagate_peers,
    ):
        """Propagate to peers"""

        # The reason you must separate this for loop here
        # is because propagation ranks do not take into account peering
        # It'd be impossible to take into account peering
        # since different customers peer to different ranks
        # So first do customer to provider propagation, then peer propagation
        for as_obj in self.as_graph:
            if as_obj.asn in valid_propagate_peers:
                as_obj.policy.propagate_to_peers()
        for as_obj in self.as_graph:
            if as_obj.asn in valid_propagate_peers:
                as_obj.policy.process_incoming_anns(
                    from_rel=PyRelationships.PEERS,
                    propagation_round=propagation_round,
                    scenario=scenario,
                )

    def _propagate_to_customers(self, propagation_round: int, scenario: "Scenario", valid_propagate_down):
        """Propagate to customers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        # So here we start at the highest rank(input_clique) and propagate down
        for i, rank in enumerate(reversed(self.as_graph.propagation_ranks)):
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    if as_obj.asn in valid_propagate_down:
                        as_obj.policy.process_incoming_anns(
                            from_rel=PyRelationships.PROVIDERS,
                            propagation_round=propagation_round,
                            scenario=scenario,
                        )
            for as_obj in rank:
                if as_obj.asn in valid_propagate_down:
                   as_obj.policy.propagate_to_customers()

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return dict(vars(self))

    @classmethod
    def __from_yaml_dict__(
        cls: type["SimulationEngine"], dct: dict[str, Any], yaml_tag: Any
    ) -> "SimulationEngine":
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)


class OptimizedAnnouncement:
    """BGP Announcement"""

    __slots__ = ("prefix", "as_path", "recv_relationship")

    def __init__(self, prefix, as_path, recv_relationship):
        self.prefix = prefix
        self.as_path = as_path
        self.recv_relationship = recv_relationship

    def prefix_path_attributes_eq(self, ann: Optional["PyAnnouncement"]) -> bool:
        """Checks prefix and as path equivalency"""

        if ann is None:
            return False
        elif isinstance(ann, PyAnnouncement):
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)
        else:
            raise NotImplementedError

    def copy(
        self, overwrite_default_kwargs: Optional[dict[Any, Any]] = None
    ) -> "PyAnnouncement":
        """Creates a new ann with proper sim attrs"""

        # Replace seed asn and traceback end every time by default
        kwargs = {"prefix": self.prefix, "as_path": self.as_path, "recv_relationship": self.recv_relationship}
        if overwrite_default_kwargs:
            kwargs.update(overwrite_default_kwargs)
        # Mypy says it gets this wrong
        # https://github.com/microsoft/pyright/issues/1047#issue-705124399
        return OptimizedAnnouncement(**kwargs)  # type: ignore

    @property
    def origin(self) -> int:
        """Returns the origin of the announcement"""

        return self.as_path[-1]

    def __str__(self) -> str:
        return f"{self.prefix} {self.as_path} {self.recv_relationship}"

def get_cone(as_obj, cone_dict, as_graph, relationship) -> set[int]:
    """Recursively determines the cone size of an as"""

    if as_obj.asn in cone_dict:
        return cone_dict[as_obj.asn]
    else:
        cone_dict[as_obj.asn] = set([as_obj.asn])
        for neighbor in getattr(as_obj, relationship):
            cone_dict[as_obj.asn].add(neighbor.asn)
            get_cone(neighbor, cone_dict, as_graph, relationship)
            cone_dict[as_obj.asn].update(cone_dict[neighbor.asn])
    return cone_dict[as_obj.asn]

as_graph = CAIDAASGraphConstructor().run()
# Python anns
import csv
anns = list()
with open("/home/anon/work/c/BGPExtrapolator/build/BGPExtrapolator/TestCases/RealData-Announcements_4000.tsv") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        as_path = [int(x) for x in row["as_path"].replace("}", "").replace("{", "").split(",")]
        if as_path[-1] in as_graph.as_dict:
            anns.append(
                PyAnn(
                    prefix=row["prefix"],
                    as_path=[as_path[-1]],
                    timestamp=0,
                    seed_asn=as_path[-1],
                    roa_valid_length=None,
                    roa_origin=None,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        else:
            print("excluding")
anns = anns[:1000]
print(len(anns))

anns = list()
with open("/home/anon/work/c/BGPExtrapolator/build/BGPExtrapolator/TestCases/RealData-Announcements_4000.tsv") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        as_path = [int(x) for x in row["as_path"].replace("}", "").replace("{", "").split(",")]
        if as_path[-1] in as_graph.as_dict:
            anns.append(
                OptimizedAnnouncement(
                    prefix=int(row["prefix_block_id"]),
                    as_path=[as_path[-1],],
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        else:
            print("excluding")
anns = anns[:1000]
print(len(anns))

# anns = [
#     PyAnn(
#         prefix="1.0.6.0/24",
#         as_path=[38803],
#         timestamp=0,
#         seed_asn=38803,
#         roa_valid_length=None,
#         roa_origin=None,
#         recv_relationship=Relationships.ORIGIN,
#     )
# ]

customer_cone_dict = dict()
valid_propagate_up = get_cone(as_graph.as_dict[174], customer_cone_dict, as_graph, "customers")
for peer_obj in as_graph.as_dict[174].peers:
    valid_propagate_up.update(get_cone(peer_obj, customer_cone_dict, as_graph, "customers"))
for provider_obj in as_graph.as_dict[174].providers:
    valid_propagate_up.update(get_cone(provider_obj, customer_cone_dict, as_graph, "customers"))

print(f"before intersecting with provider cone of anns {len(valid_propagate_up)}")
raise NotImplementedError("Must also propagate up to the peers of everyone in the provider cone")
raise NotImplementedError("to speed up this calculation - propagate up for the provider cone of the ann is about the same as the provider cone of the ann interesected with the customers of the vantage point")
# Now get provider cone of anns
ann_provider_cone = set()
provider_cone_dict = dict()
print("This will also break for seeding along as path")
for ann in anns:
    seed_asn = getattr(ann, "seed_asn", ann.as_path[-1])
    ann_provider_cone.update(get_cone(as_graph.as_dict[seed_asn], provider_cone_dict, as_graph, "providers"))
print(f"ann provider cone {len(ann_provider_cone)}")
valid_propagate_up = valid_propagate_up.intersection(ann_provider_cone)
print(f"after intersecting with provider cone of anns {len(valid_propagate_up)}")

provider_cone = get_cone(as_graph.as_dict[174], provider_cone_dict, as_graph, "providers")
valid_propagate_down = provider_cone
# If this is the only one in the set, don't propagate it
if valid_propagate_down == set([174]):
    valid_propagate_down = set()
print(f"valid propagate down {len(valid_propagate_down)}")
valid_propagate_peers = set()
for asn in set([174]) | valid_propagate_down:
    for peer in as_graph.as_dict[asn].peers:
        valid_propagate_peers.add(peer.asn)


print(f"valid peers {len(valid_propagate_peers)}")

# print(f"valid peers post intersection{len(valid_propagate_peers.intersection(ann_provider_cone))}")

input("waot")

# py_sim_engine = PySimulationEngine(as_graph)
# py_sim_engine.setup(anns)
# start = time.perf_counter()
# py_sim_engine.run()
# input(str(as_graph.as_dict[174].policy._local_rib))
# print(time.perf_counter() - start)


exr_sim_engine = ExrPySimulationEngine(as_graph)
exr_sim_engine.setup(anns)
start = time.perf_counter()
# input(38803 in valid_propagate_up)
exr_sim_engine._propagate_to_providers(0, None, valid_propagate_up)
exr_sim_engine._propagate_to_peers(0, None, valid_propagate_peers)
exr_sim_engine._propagate_to_customers(0, None, valid_propagate_down)
# input(str(as_graph.as_dict[174].policy._local_rib))

print(time.perf_counter() - start)







as_graph = CAIDAASGraphConstructor().run()
# Python anns
import csv
anns = list()
with open("/home/anon/work/c/BGPExtrapolator/build/BGPExtrapolator/TestCases/RealData-Announcements_4000.tsv") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        as_path = [int(x) for x in row["as_path"].replace("}", "").replace("{", "").split(",")]
        if as_path[-1] in as_graph.as_dict:
            origin = as_path[-1]
        else:
            origin = 1
        anns.append(
            CPPAnn(
                prefix_block_id=int(row["prefix_block_id"]),
                prefix=row["prefix"],
                as_path=[origin],
                timestamp=0,
                seed_asn=origin,
                roa_valid_length=None,
                roa_origin=None,
                recv_relationship=CPPRelationships.ORIGIN,
                withdraw=False,
                traceback_end=False,
                communities=list()
            )
        )
# anns = anns[:1000]
print(len(anns))
# anns = [
#     PyAnn(
#         prefix="1.0.6.0/24",
#         as_path=[38803],
#         timestamp=0,
#         seed_asn=38803,
#         roa_valid_length=None,
#         roa_origin=None,
#         recv_relationship=Relationships.ORIGIN,
#     )
# ]

customer_cone_dict = dict()
valid_propagate_up = get_cone(as_graph.as_dict[174], customer_cone_dict, as_graph, "customers")
for peer_obj in as_graph.as_dict[174].peers:
    valid_propagate_up.update(get_cone(peer_obj, customer_cone_dict, as_graph, "customers"))
for provider_obj in as_graph.as_dict[174].providers:
    valid_propagate_up.update(get_cone(provider_obj, customer_cone_dict, as_graph, "customers"))

print(f"before intersecting with provider cone of anns {len(valid_propagate_up)}")
# Now get provider cone of anns
ann_provider_cone = set()
provider_cone_dict = dict()
for ann in anns:
    ann_provider_cone.update(get_cone(as_graph.as_dict[ann.seed_asn], provider_cone_dict, as_graph, "providers"))
print(f"ann provider cone {len(ann_provider_cone)}")
valid_propagate_up = valid_propagate_up.intersection(ann_provider_cone)
print(f"after intersecting with provider cone of anns {len(valid_propagate_up)}")

provider_cone = get_cone(as_graph.as_dict[174], provider_cone_dict, as_graph, "providers")
valid_propagate_down = provider_cone
# If this is the only one in the set, don't propagate it
if valid_propagate_down == set([174]):
    valid_propagate_down = set()
print(f"valid propagate down {len(valid_propagate_down)}")
valid_propagate_peers = set()
for asn in set([174]) | valid_propagate_down:
    for peer in as_graph.as_dict[asn].peers:
        valid_propagate_peers.add(peer.asn)


print(f"valid peers {len(valid_propagate_peers)}")



input("waot")

# py_sim_engine = PySimulationEngine(as_graph)
# py_sim_engine.setup(anns)
# start = time.perf_counter()
# py_sim_engine.run()
# input(str(as_graph.as_dict[174].policy._local_rib))
# print(time.perf_counter() - start)


cpp_sim_engine = CPPSimulationEngine(as_graph)
cpp_sim_engine.setup(anns)
start = time.perf_counter()
# input(38803 in valid_propagate_up)
cpp_sim_engine.run(0, None, valid_propagate_up, valid_propagate_peers, valid_propagate_down)
# input(str(as_graph.as_dict[174].policy._local_rib))

print(time.perf_counter() - start)
raise NotImplementedError("check anns at each as")
