from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import logging
from multiprocessing import Pool, cpu_count
import random

from lib_caida_collector import CaidaCollector

from .attacks import Attack
from .data_point import DataPoint
from .scenario import Scenario

from ..engine import BGPPolicy, BGPAS, SimulatorEngine

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

    def run(self, parse_cpus, _dir, debug=False):
        self.data_points = dict()
        self._dir = _dir

        if debug:
            # Done just to get subgraphs, change this later
            engine = CaidaCollector(BaseASCls=BGPAS,
                                    GraphCls=SimulatorEngine,
                                    _dir=_dir,
                                    _dir_exist_ok=True).run(tsv=False)

            self.subgraphs = self._get_subgraphs(engine)
            self._validate_subgraphs()
           
            for x in self.percent_adoptions:
                self.data_points.update(self._run_adoption_percentage(x,
                                                                      engine=engine,
                                                                      subgraphs=self.subgraphs))
        else:
            print("About to run pool")
            # Pool is much faster than ProcessPoolExecutor
            with Pool(parse_cpus) as pool:
                for result in pool.map(self._run_adoption_percentage,
                                       self.percent_adoptions):
                    self.data_points.update(result)

        print("\nGraph complete")
        if not debug:
            # Done just to get subgraphs, change this later
            engine = CaidaCollector(BaseASCls=BGPAS,
                                    GraphCls=SimulatorEngine,
                                    _dir=_dir,
                                    _dir_exist_ok=True).run(tsv=False)

            self.subgraphs = self._get_subgraphs(engine)
            self._validate_subgraphs()

    def _run_adoption_percentage(self, percent_adopt, engine=None, subgraphs=None):
        if engine is None:
            # Engine is not picklable or dillable AT ALL, so do it here
            # Changing recursion depth does nothing
            # Making nothing a reference does nothing
            engine = CaidaCollector(BaseASCls=BGPAS,
                                    GraphCls=SimulatorEngine,
                                    _dir=self._dir,
                                    _dir_exist_ok=True).run(tsv=False)

        if subgraphs is None:
            self.subgraphs = self._get_subgraphs(engine) 
            self._validate_subgraphs()

        data_points = dict()

        for trial in range(self.num_trials):
            print(f"Percent adopt {percent_adopt} trial {trial}        ", end="\r")
            og_attack = self._get_attack()
            adopting_asns = self._get_adopting_ases(percent_adopt, og_attack)
            assert len(adopting_asns) != 0
            #print("Selected adopting")
            for PolicyCls in self.adopt_policies:
                # In case the attack has state we deepcopy it so that it doesn't remain from policy to policy
                attack = deepcopy(og_attack)
                self._replace_engine_policies({x: PolicyCls for x in adopting_asns}, engine)
                for propagation_round in range(self.propagation_rounds):
                    # Generate the test
                    scenario = Scenario(trial=trial, engine=engine, attack=attack)
                    #print("about to run")
                    # Run test, remove reference to engine and return it
                    scenario.run(self.subgraphs, propagation_round)
                    #print("ran")
                    # Get data point - just a frozen data class
                    # Just makes it easier to access properties later
                    dp = DataPoint(percent_adopt, PolicyCls, propagation_round)
                    # Append the test to all tests for that data point
                    data_points[dp] = data_points.get(dp, [])
                    data_points[dp].append(scenario)
                    for func in attack.post_run_hooks:
                        func(engine, dp)
        return data_points

    def _get_subgraphs(self, engine):
        """Returns all the subgraphs that you want to keep track of"""

        #top_level = set(x.asn for x in sorted(engine.as_dict.values(),
        #                       key=lambda x: x.customer_cone_size,
        #                       reverse=True)[:100])
        top_level = set(x.asn for x in engine if x.input_clique)
        stubs_and_mh = set([x.asn for x in engine if x.stub or x.multihomed])

        subgraphs = dict()
        # Remove sets to make keeping deterministic properties easier
        subgraphs["etc"] =  set([x.asn for x in engine
                                 if x.asn not in top_level
                                 and x.asn not in stubs_and_mh])
        subgraphs["input_clique"] = top_level
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
                logging.debug("ASNs adopting rounded down to 0, increasing it to 1")
                k = 1
            elif k == len(possible_adopting_ases):
                logging.debug("K is 100%, changing to 100% -1")
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
        for asn, as_obj in base_engine.as_dict.items():
            as_obj.policy = as_policy_dict.get(asn, self.base_policy)()        

    @property
    def total_scenarios(self):
        total_scenarios = self.num_trials * len(self.percent_adoptions)
        total_scenarios *= len(self.adopt_policies)
        total_scenarios *= self.propagation_rounds
        return total_scenarios
