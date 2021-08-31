from lib_utils import Base


class Simulator(Base):
    """Runs simulations for BGP attack/defend scenarios"""

    def run(self,
            num_trials=1,
            graph_lines=[]):
        """Downloads relationship data, runs simulation"""

@dataclass(frozen=True)
class DataPoint:
    percent_adoption: float
    ASCls: AS
    propagation_round: int

class Test:
    def __init__(self, trial=None, engine=None):
        self.trial = trial
        self.engine = engine

    def run(self):
        # Run engine
        self.engine.run()
        self._collect_data()
        # delete engine from attrs so that garbage collector can come
        engine = self.engine
        del self.engine
        # Return engine so that propogation can run again
        return engine

    def _collect_data(self):
        """Collects data about the test run before engine is deleted"""

        pass


class Graph:

    DataPtCls = 

    def __init__(self, perc_adopts, as_classes, as_dict, total_rounds=1):
        assert isinstance(perc_adopts, list)
        self.percent_adoptions = perc_adopts
        self.as_classes = as_classes
        # Why total rounds? Because some atk/def scenarios might require
        # More than one round of propogation
        self.total_rounds = total_rounds
        self.data_points = self._get_data_points()
        self.subgraphs: dict = self._get_subgraphs(as_dict)
        self._validate_subgraphs()

    def run(self, num_trials: int):
        for trial in range(num_trials):
            for percent_adopt in self.percent_adoptions:
                attack = self._get_attack()
                adopting_asns = self._get_adopting_ases(percent_adopt, attack)
                for ASCls in self.as_classes:
                    engine = self._get_engine({x: ASCls for x in adopting_asns})
                    for propogation_round in range(self.total_rounds):
                        # Generate the test
                        test = Test(trial=trial, engine=engine)
                        # Run test, remove reference to engine
                        engine = test.run()
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
            for ASCls in self.as_classes:
                for round_num in self.total_rounds:
                    dp = DataPoint(percent_adoption, ASCls, propagation_round)
                    data_points[dp] = list()
        return data_points

    def _get_subgraphs(self):
        """Returns all the subgraphs that you want to keep track of"""

        msg = "If there as_rank==0, we must do <100, not <=100 on next line"
        assert not any([x.as_rank == 0 for x in self.as_dict]), msg
        top_level = set([x.asn for x in self.as_dict if x.as_rank <= 100])
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

    def _get_engine(self, as_classes: dict):
        # Make engine here!

        pass
