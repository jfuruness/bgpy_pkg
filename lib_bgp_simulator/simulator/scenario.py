import ipaddress
from ..enums import Relationships, Outcomes


class Scenario:
    def __init__(self, trial=None, engine=None, attack=None, profiler=None):
        self.trial = trial
        self.engine = engine
        self.attack = attack
        self.data = dict()
        self.profiler = profiler

    def run(self, subgraphs, propagation_round: int):
        # Run engine
        self.engine.run(self.attack.announcements,
                        propagation_round=propagation_round,
                        attack=self.attack)
        #print("Engine finished running")
        self._collect_data(subgraphs)
        # delete engine from attrs so that garbage collector can come
        # NOTE that if there are multiple propagation rounds, the engine
        # Will still be there
        engine = self.engine
        del self.engine

    def _collect_data(self, subgraphs):
        """Collects data about the test run before engine is deleted"""

        policies = set([x.name for x in self.engine])
        all_data = {"data": dict(), "totals": dict()}
        cache = dict()
        for k, subgraph_asns in subgraphs.items():
            all_data["data"][k] = self._get_outcomes(policies, subgraph_asns, cache)
            all_data["totals"][k] = self._get_policy_totals(policies, subgraph_asns)
        self.data = all_data
        #from pprint import pprint
        #pprint(all_data)

    def _get_outcomes(self, policies, subgraph_asns, cache):
        outcomes = {x: {y: 0 for y in policies}
                    for x in list(Outcomes)}
        # Most specific to least specific
        ordered_prefixes = self._get_ordered_prefixes()

        countable_asns = subgraph_asns.difference(self.attack.uncountable_asns)

        for asn in countable_asns:
            as_obj = self.engine.as_dict[asn]
            # Get the attack outcome
            outcome = self._get_atk_outcome(as_obj, ordered_prefixes, 0, cache)
            # Incriment the outcome and policy by 1
            outcomes[outcome][as_obj.name] += 1
        return outcomes

    def _get_atk_outcome(self, as_obj, ordered_prefixes, path_len, cache):
        assert path_len < 128, "Path is too long, probably looping"

        if as_obj.asn in cache:
            return cache[as_obj.asn]

        # Get most specific announcement, or empty RIB
        most_specific_ann = self._get_most_specific_ann(as_obj, ordered_prefixes)
        # Determine the outcome of the attack
        attack_outcome = self.attack.determine_outcome(as_obj, most_specific_ann)
        if not attack_outcome:
            # Continue tracing back by getting the last AS
            new_as_obj = self.engine.as_dict[most_specific_ann.as_path[1]]
            attack_outcome = self._get_atk_outcome(new_as_obj, ordered_prefixes, path_len + 1, cache)

        assert attack_outcome is not None, "Attack should be disconnected, why is this wrong?"

        cache[as_obj.asn] = attack_outcome

        return attack_outcome

    def _get_ordered_prefixes(self):
        prefixes = set()
        for ann in self.attack.announcements:
            prefixes.add(ann.prefix)

        assert len(prefixes) > 0
        # Prefixes with most specific subprefix first
        return tuple(sorted(prefixes, key=lambda x: ipaddress.ip_network(x).num_addresses))

    def _get_most_specific_ann(self, as_obj, ordered_prefixes):
        for prefix in ordered_prefixes:
            most_specific_prefix = as_obj.local_rib.get_ann(prefix)
            if most_specific_prefix is not None:
                break
        return most_specific_prefix

    def _get_policy_totals(self, policy_names, subgraph_asns):
        """Determines the total amount of ASes per policy"""

        totals = {x: 0 for x in policy_names}
        for asn in subgraph_asns.difference(self.attack.uncountable_asns):
            totals[self.engine.as_dict[asn].name] += 1
        return totals
