from .outcomes import Outcomes
from .relationships import Relationships


class Test:
    def __init__(self, trial=None, engine=None, attack=None):
        self.trial = trial
        self.engine = engine
        self.attack = attack

    def run(self, subgraphs):
        # Run engine
        self.engine.run(self.attack.announcements)
        self._collect_data(subgraphs)
        # delete engine from attrs so that garbage collector can come
        engine = self.engine
        del self.engine
        # Return engine so that propogation can run again
        return engine

    def _collect_data(self, subgraphs):
        """Collects data about the test run before engine is deleted"""

        assert False, "Must also do by subgraphs ughhhhh"
        policies = set([x.policy.name for x in self.engine.as_dict.values()])
        all_data = {"data": dict(), "meta": dict()}
        for k, subgraph_asns in subgraphs.items():
            all_data["data"][k] = self._get_outcomes(policies, subgraph_asns)
            all_data["meta"][k] = {"total": l

    def _get_outcomes(self, policies, subgraph_asns):
        outcomes = {x: {y: 0 for y in policies}
                    for x in list(Outcome)}
        # Most specific to least specific
        ordered_prefixes = self._get_ordered_prefixes()
        for og_as_obj in self.engine.as_dict.values():
            if og_as_obj.asn not in subgraph_asns:
                continue
            final_as_obj, has_rib = self._get_final_as(og_as_obj, ordered_prefixes, outcomes)
            self._store_outcome(final_as_obj, has_rib, og_as_obj, outcomes)
        return outcomes

    def _get_final_as(self, as_obj, ordered_prefixes, outcomes):
        has_rib = True
        # Loop all the way through to the end
        while as_obj.recv_relationships != Relationships.ORIGIN:
            # Get most specific announcement, or empty RIB
            longest_ann = self._get_longest_ann(as_obj, ordered_prefixes)
            if longest_ann is None:
                has_rib = False
                break
            # Continue looping by getting the last AS
            as_obj = self.engine.as_dict[longest_ann.as_path[1]]
        return as_obj, has_rib

    def _store_outcome(self, as_obj, has_rib, og_as_obj, outcomes):
        if has_rib:
            # Store the outcome so long as there is a rib
            if as_obj.asn == self.attack.attacker_asn:
                outcomes[Outcome.HIJACKED][og_as_obj.policy.name] += 1
            if as_obj.asn == self.attack.victim_asn:
                outcomes[Outcome.NOT_HIJACKED][og_as_obj.policy.name] += 1
            else:
                outcomes[Outcome.DISCONNECTED][og_as_obj.policy.name] += 1
        else:
            outcomes[Outcome.DISCONNECTED][og_as_obj.policy.name] += 1

    def _get_ordered_prefixes(self):
        prefixes = set()
        for ann in self.attack.announcements:
            prefixes.add(ann.prefix)

        # Prefixes with most specific subprefix first
        return tuple(sorted(prefixes, reverse=True))

    def _get_longest_ann(self, ordered_prefixes):
        for prefix in ordered_prefixes:
            most_specific_prefix = as_obj.local_rib.get(prefix)
            if most_specific_prefix is not None:
                break
        return most_specific_prefix
