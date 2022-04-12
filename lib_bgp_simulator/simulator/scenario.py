from collections import defaultdict

import ipaddress
from ..enums import Outcomes
from ..engine import BGPAS


class Scenario:
    """A single simulator engine run scenario"""

    def __init__(self,
                 trial=None,
                 engine=None,
                 engine_input=None,
                 profiler=None):
        """Stores all attributes"""

        self.trial = trial
        self.engine = engine
        self.engine_input = engine_input
        self.data = dict()
        self.profiler = profiler

    def run(self, subgraphs, propagation_round: int):
        """Runs engine, gets stats from run, deletes engine for space"""

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
        # Delete the adopting_asns for the same reason.
        # This does not cause problems for multiple rounds because the AS
        # classes are already set.
        if hasattr(self.engine_input, 'adopting_asns'):
            del self.engine_input.adopting_asns

        return traceback_outcomes

    def _collect_data(self, subgraphs):
        """Collects data about the test run before engine is deleted"""

        policies = set([x.name for x in self.engine])
        traceback_cache = dict()
        # {subgraph_name: {outcome: {policy: percentage}}}
        self.outcome_policy_percentages = dict()
        for subg_name, subgraph_asns in subgraphs.items():
            # Get all trackable ASNs
            countable_asns = subgraph_asns.difference(
                self.engine_input.uncountable_asns)
            # {outcome: {policy: total}
            outcome_totals = self._get_outcomes(policies,
                                                countable_asns,
                                                traceback_cache)
            # {policy: total number of countable asn's for that policy}
            total_ases = self._get_policy_totals(policies, countable_asns)

            # Convert the numbers to percentages
            percentage_outcomes = defaultdict(dict)
            for outcome in list(Outcomes):
                for policy in policies:
                    outcome_policy_total = outcome_totals[outcome][policy]

                    policy_total = total_ases[policy]

                    percentage = outcome_policy_total * 100 / policy_total
                    percentage_outcomes[outcome][policy] = percentage

            self.outcome_policy_percentages[subg_name] = percentage_outcomes
        return traceback_cache

    def _get_outcomes(self, policies, countable_asns, traceback_cache):
        """Traceback to the origin AS and get the outcome of the attack"""

        # {outcome: {policy: total_for_policy}}
        outcomes = {x: {y: 0 for y in policies}
                    for x in list(Outcomes)}
        # Most specific to least specific
        ordered_prefixes = self._get_ordered_prefixes()

        for asn in countable_asns:
            # Get the AS object
            as_obj = self.engine.as_dict[asn]
            # Get the attack outcome
            outcome = self._get_atk_outcome(as_obj,
                                            ordered_prefixes,
                                            0,
                                            traceback_cache)
            # Incriment the outcome and policy by 1
            outcomes[outcome][as_obj.name] += 1
        return outcomes

    def _get_atk_outcome(self,
                         as_obj,
                         ordered_prefixes,
                         path_len,
                         traceback_cache):
        """Get the attack outcome for a specific AS for most specific prefix"""

        assert path_len < 128, "Path is too long, probably looping"

        # Don't bother tracing back from the same AS twice
        if as_obj.asn in traceback_cache:
            return traceback_cache[as_obj.asn]

        # Get most specific announcement, or empty RIB
        most_specific_ann = self._get_most_specific_ann(as_obj,
                                                        ordered_prefixes)
        # Determine the outcome of the attack
        attack_outcome = self.engine_input.determine_outcome(as_obj,
                                                             most_specific_ann)
        # If we don't have an attack outcome, recursively retrace to origin
        if not attack_outcome:
            # Continue tracing back by getting the last AS
            new_as_obj = self.engine.as_dict[most_specific_ann.as_path[1]]
            if not isinstance(as_obj, BGPAS):
                msg = ("Path manipulation not allowed for BGPSimpleAS. "
                       "Consider inheriting from BGPAS instead")
                assert new_as_obj in as_obj.neighbors, msg
            # Recursively retrace to origin
            attack_outcome = self._get_atk_outcome(new_as_obj,
                                                   ordered_prefixes,
                                                   path_len + 1,
                                                   traceback_cache)
            msg = "Path manipulation attack with no traceback end?"
            assert (attack_outcome is not None
                    or new_as_obj in as_obj.neighbors)

        assert attack_outcome is not None, "Attack should be disconnected?"

        # Cache the outcome of the traceback
        traceback_cache[as_obj.asn] = attack_outcome

        return attack_outcome

    def _get_ordered_prefixes(self):
        """Returns prefixes in order of specificity"""

        prefixes = set()
        for ann in self.engine_input.announcements:
            prefixes.add(ann.prefix)

        assert len(prefixes) > 0
        # Prefixes with most specific subprefix first
        return tuple(sorted(prefixes,
                            key=lambda x: ipaddress.ip_network(x).num_addresses
                            ))

    def _get_most_specific_ann(self, as_obj, ordered_prefixes):
        """Gets the most specific announcement at an AS"""

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
