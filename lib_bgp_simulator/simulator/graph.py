from copy import deepcopy

class Graph:
    def __init__(self,
                 perc_adopts,
                 as_policies,
                 base_engine,
                 propagation_rounds=1):
        assert isinstance(percent_adoptions, list)
        self.percent_adoptions = percent_adoptions
        self.as_policies = as_policies
        # Why propagation rounds? Because some atk/def scenarios might require
        # More than one round of propogation
        self.propagation_rounds = propagation_rounds
        self.base_engine = deepcopy(base_engine)
        self.data_points = self._get_data_points()
        self.subgraphs: dict = self._get_subgraphs(as_dict)
        self._validate_subgraphs()

    def run(self, num_trials: int):
        for trial in range(num_trials):
            for percent_adopt in self.percent_adoptions:
                attack = self._get_attack()
                adopting_asns = self._get_adopting_ases(percent_adopt, attack)
                for PolicyCls in self.policy_classes:
                    engine = self._get_engine({x: PolicyCls for x in adopting_asns})
                    for propogation_round in range(self.propagation_rounds):
                        # Generate the test
                        test = Test(trial=trial, engine=engine, attack=attack)
                        # Run test, remove reference to engine and return it
                        engine = test.run(self.subgraphs)
                        # Get data point - just a frozen data class
                        # Just makes it easier to access properties later
                        dp = DataPoint(percent_adopt, ASCls, propogation_round)
                        # Append the test to all tests for that data point
                        self.data_pts[dp].append(test)

    def _get_data_points(self):
        """Returns all data points for this graph

        each of which contains a list of trials
        """

        data_points = dict()
        for percent_adoption in self.percent_adoptions:
            for Policy in self.as_policies:
                for propagation_round in self.propagation_rounds:
                    dp = DataPoint(percent_adoption, Policy, propagation_round)
                    data_points[dp] = list()
        return data_points

    def _get_subgraphs(self):
        """Returns all the subgraphs that you want to keep track of"""

        top_level = set(sorted(self.as_dict.values(),
                               key=lambda x: x.as_rank)[:100])
        stubs_and_mh = set([x.asn for x in self.as_dict
                            if any((x.stub, x.multihomed))])

        # Remove sets to make keeping deterministic properties easier
        self.subgraphs["etc"] =  set([x.asn for x in self.bgp_dag
                                      if x not in (top_level | stubs_and_mh)])
        self.subgraphs["top_100"] = top_level
        self.subgraphs["stubs_and_mb"] = stubs_and_mh

    def _validate_subgraphs(self):
        """Makes sure subgraphs are mutually exclusive and contain ASNs"""

        all_ases = []
        for subgraph_asns in self.subgraphs:
            msg = "Subgraphs must be sets for fast lookups"
            assert isinstance(subgraph_asns, set), msg
            all_ases.extend(subgraph_asns)
        for x in all_ases:
            assert isinstance(x, int), "Subgraph doesn't contain ASNs"

        msg = "subgraphs not mutually exclusive"
        assert len(all_ases) == len(set(all_ases)), msg
 
    def _get_adopting_ases(self, percent_adopt) -> list:
        """Return a list of adopting ASNs that aren't attackers"""

        asns_adopting = list()
        for subgraph_asns in self.subgraphs.values():
            # Get all possible ASes that could adopt
            possible_ases = self._get_possible_adopting_asns(subgraph_asns,
                                                             attack)

            # N choose k, k is number of ASNs that will adopt
            k = int(len(possible_ases) * percent_adopt)
            if k == 0:
                logging.warning("ASNs adopting rounded down to 0")

            asns_adopting.extend(random.sample(possible_adopting_ases, k))
        return asns_adopting

    def _get_possible_adopting_asns(self, subgraph_asns: set, attack: Attack):
        """Returns the set of all possible adopting ASNs

        Done here so that you can easily override to also remove victims
        from possible adopters
        """

        # Return all ASes other than the attacker
        return subgraph_asns.difference([attack.attacker])

    def _get_engine(self, as_policies: dict):
        # Make engine here!

        new_engine = deepcopy(self.base_engine)
        for asn, PolicyCls in as_policies.items():
            new_engine.as_dict[asn].policy = PolicyCls()
        return new_engine
