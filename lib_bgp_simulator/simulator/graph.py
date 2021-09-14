from copy import deepcopy
import logging
import random

from .attacks import Attack
from .data_point import DataPoint
from .scenario import Scenario

from ..engine import BGPPolicy

class Graph:
    from .graph_writer import aggregate_and_write
    from .graph_writer import _write

    def __init__(self,
                 percent_adoptions=[1, 5, 10, 20, 30, 50, 75, 99],
                 adopt_policies=[],
                 AttackCls=None,
                 num_trials=1,
                 propagation_rounds=1,
                 base_policy=BGPPolicy):
        assert isinstance(percent_adoptions, list)
        self.percent_adoptions = percent_adoptions
        self.adopt_policies = adopt_policies
        self.num_trials = num_trials
        # Why propagation rounds? Because some atk/def scenarios might require
        # More than one round of propagation
        self.propagation_rounds = propagation_rounds
        self.AttackCls = AttackCls
        self.base_policy = base_policy

    def run(self, engine, pbar):
        # Get data points and subgraphs
        self.data_points = self._get_data_points()
        self.subgraphs: dict = self._get_subgraphs(engine)
        self._validate_subgraphs()

        # Get all the tests and run them
        for trial in range(self.num_trials):
            for percent_adopt in self.percent_adoptions:
                attack = self._get_attack()
                print("adopting ases")
                adopting_asns = self._get_adopting_ases(percent_adopt, attack)
                print("Selected adopting")
                for PolicyCls in self.adopt_policies:
                    self._replace_engine_policies({x: PolicyCls for x in adopting_asns}, engine)
                    print("got engine")
                    for propagation_round in range(self.propagation_rounds):
                        # Generate the test
                        scenario = Scenario(trial=trial, engine=engine, attack=attack)
                        print("about to run")
                        # Run test, remove reference to engine and return it
                        scenario.run(self.subgraphs)
                        print("ran")
                        # Get data point - just a frozen data class
                        # Just makes it easier to access properties later
                        dp = DataPoint(percent_adopt, PolicyCls, propagation_round)
                        # Append the test to all tests for that data point
                        self.data_points[dp].append(scenario)
                        pbar.update()

    def _get_data_points(self):
        """Returns all data points for this graph

        each of which contains a list of trials
        """

        data_points = dict()
        for percent_adoption in self.percent_adoptions:
            for Policy in self.adopt_policies:
                for propagation_round in range(self.propagation_rounds):
                    dp = DataPoint(percent_adoption, Policy, propagation_round)
                    data_points[dp] = list()
        return data_points

    def _get_subgraphs(self, engine):
        """Returns all the subgraphs that you want to keep track of"""

        top_level = set(x.asn for x in sorted(engine.as_dict.values(),
                               key=lambda x: x.customer_cone_size,
                               reverse=True)[:100])
        stubs_and_mh = set([x.asn for x in engine.as_dict.values()
                            if x.stub or x.multihomed])

        subgraphs = dict()
        # Remove sets to make keeping deterministic properties easier
        subgraphs["etc"] =  set([x.asn for x in engine.as_dict.values()
                                      if x.asn not in top_level
                                        and x.asn not in stubs_and_mh])
        subgraphs["top_100"] = top_level
        subgraphs["stubs_and_mh"] = stubs_and_mh
        return subgraphs

    def _validate_subgraphs(self):
        """Makes sure subgraphs are mutually exclusive and contain ASNs"""

        all_ases = []
        for subgraph_asns in self.subgraphs.values():
            msg = "Subgraphs must be sets for fast lookups"
            assert isinstance(subgraph_asns, set), msg
            all_ases.extend(subgraph_asns)
        for x in all_ases:
            assert isinstance(x, int), "Subgraph doesn't contain ASNs"

        msg = "subgraphs not mutually exclusive"
        assert len(all_ases) == len(set(all_ases)), msg

    def _get_attack(self):
        return self.AttackCls(*random.sample(self.subgraphs["stubs_and_mh"], 2))
 
    def _get_adopting_ases(self, percent_adopt, attack) -> list:
        """Return a list of adopting ASNs that aren't attackers"""

        asns_adopting = list()
        for subgraph_asns in self.subgraphs.values():
            # Get all possible ASes that could adopt
            possible_adopting_ases = self._get_possible_adopting_asns(subgraph_asns,
                                                             attack)

            # N choose k, k is number of ASNs that will adopt
            k = len(possible_adopting_ases) * percent_adopt // 100
            if k == 0:
                logging.warning("ASNs adopting rounded down to 0, increasing it to 1")
                k = 1
            elif k == len(possible_adopting_ases):
                logging.warning("K is 100%, changing to 100% -1")
                k -= 1

            asns_adopting.extend(random.sample(possible_adopting_ases, k))
        return asns_adopting

    def _get_possible_adopting_asns(self, subgraph_asns: set, attack: Attack):
        """Returns the set of all possible adopting ASNs

        Done here so that you can easily override to also remove victims
        from possible adopters
        """

        # Return all ASes other than the attacker
        return subgraph_asns.difference([attack.attacker_asn])

    def _replace_engine_policies(self, as_policy_dict, base_engine):
        # Make engine here!
        for asn, as_obj in base_engine.as_dict.items():
            as_obj.policy = as_policy_dict.get(asn, self.base_policy)()        

    @property
    def total_scenarios(self):
        total_scenarios = self.num_trials * len(self.percent_adoptions)
        total_scenarios *= len(self.adopt_policies)
        total_scenarios *= self.propagation_rounds
        return total_scenarios
