from collections import defaultdict

import ipaddress
from ..enums import Outcomes


class Scenario:
    def __init__(self, trial=None, engine=None, engine_input=None, profiler=None):
        self.trial = trial
        self.engine = engine
        self.engine_input = engine_input
        self.data = dict()
        self.profiler = profiler

    def run(self, subgraphs, propagation_round: int):
        # Run engine
        self.engine.run(propagation_round=propagation_round,
                        engine_input=self.engine_input)
        traceback_outcomes = self._collect_data(subgraphs)
        # Don't count these for diagrams and such
        for uncountable_asn in self.engine_input.uncountable_asns:
            traceback_outcomes.pop(uncountable_asn, None)
        # delete engine from attrs so that garbage collector can come
        # NOTE that if there are multiple propagation rounds, the engine
        # Will still be there
        del self.engine

        return traceback_outcomes

    def _collect_data(self, subgraphs):
        """Collects data about the test run before engine is deleted"""

        policies = set([x.name for x in self.engine])
        cache = dict()
        # {subgraph_name: {outcome: {policy: percentage}}}
        self.outcome_policy_percentages = dict()
        for subg_name, subgraph_asns in subgraphs.items():
            countable_asns = subgraph_asns.difference(
                self.engine_input.uncountable_asns)

            outcome_totals = self._get_outcomes(policies,
                                                countable_asns,
                                                cache)
            total_ases = self._get_policy_totals(policies, countable_asns)

            percentage_outcomes = defaultdict(dict)
            for outcome in list(Outcomes):
                for policy in policies:
                    outcome_policy_total = outcome_totals[outcome][policy]

                    policy_total = total_ases[policy]

                    percentage = outcome_policy_total * 100 / policy_total
                    percentage_outcomes[outcome][policy] = percentage

            self.outcome_policy_percentages[subg_name] = percentage_outcomes
        return cache

    def _get_outcomes(self, policies, countable_asns, cache):
        outcomes = {x: {y: 0 for y in policies}
                    for x in list(Outcomes)}
        # Most specific to least specific
        ordered_prefixes = self._get_ordered_prefixes()

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
        most_specific_ann = self._get_most_specific_ann(as_obj,
                                                        ordered_prefixes)
        # Determine the outcome of the attack
        attack_outcome = self.engine_input.determine_outcome(as_obj,
                                                       most_specific_ann)
        if not attack_outcome:
            # Continue tracing back by getting the last AS
            new_as_obj = self.engine.as_dict[most_specific_ann.as_path[1]]
            attack_outcome = self._get_atk_outcome(new_as_obj,
                                                   ordered_prefixes,
                                                   path_len + 1,
                                                   cache)

        assert attack_outcome is not None, "Attack should be disconnected?"

        cache[as_obj.asn] = attack_outcome

        return attack_outcome

    def _get_ordered_prefixes(self):
        prefixes = set()
        for ann in self.engine_input.announcements:
            prefixes.add(ann.prefix)

        assert len(prefixes) > 0
        # Prefixes with most specific subprefix first
        return tuple(sorted(prefixes,
                            key=lambda x: ipaddress.ip_network(x).num_addresses
                            ))

    def _get_most_specific_ann(self, as_obj, ordered_prefixes):
        for prefix in ordered_prefixes:
            most_specific_prefix = as_obj._local_rib.get_ann(prefix)
            if most_specific_prefix is not None:
                break
        return most_specific_prefix

    def _get_policy_totals(self, policy_names, countable_asns):
        """Determines the total amount of ASes per policy"""

        totals = {x: 0 for x in policy_names}
        for asn in countable_asns:
            totals[self.engine.as_dict[asn].name] += 1
        return totals
