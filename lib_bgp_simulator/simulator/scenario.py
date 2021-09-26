import ipaddress
from ..enums import Relationships, Outcomes


class Scenario:
    def __init__(self, trial=None, engine=None, attack=None):
        self.trial = trial
        self.engine = engine
        self.attack = attack
        self.data = dict()

    def run(self, subgraphs, propagation_round: int):
        # Run engine
        self.engine.run(self.attack.announcements,
                        propagation_round=propagation_round)
        #print("Engine finished running")
        self._collect_data(subgraphs)
        # delete engine from attrs so that garbage collector can come
        # NOTE that if there are multiple propagation rounds, the engine
        # Will still be there
        engine = self.engine
        del self.engine

    def _collect_data(self, subgraphs):
        """Collects data about the test run before engine is deleted"""

        policies = set([x.policy.name for x in self.engine.as_dict.values()])
        all_data = {"data": dict(), "totals": dict()}
        for k, subgraph_asns in subgraphs.items():
            all_data["data"][k] = self._get_outcomes(policies, subgraph_asns)
            all_data["totals"][k] = self._get_policy_totals(policies, subgraph_asns)
        self.data = all_data
        from pprint import pprint
        pprint(all_data)


    def _get_outcomes(self, policies, subgraph_asns):
        outcomes = {x: {y: 0 for y in policies}
                    for x in list(Outcomes)}
        # Most specific to least specific
        ordered_prefixes = self._get_ordered_prefixes()
        # NOTE: this should be changed to ONLY iterate over subgraph asns
        for og_as_obj in self.engine.as_dict.values():
            if og_as_obj.asn not in subgraph_asns:
                continue
            if og_as_obj.asn in [self.attack.attacker_asn, self.attack.victim_asn]:
                continue
            final_as_obj, has_rib = self._get_final_as(og_as_obj, ordered_prefixes, outcomes)
            self._store_outcome(final_as_obj, has_rib, og_as_obj, outcomes)
        return outcomes

    def _get_final_as(self, as_obj, ordered_prefixes, outcomes):
        has_rib = True
        max_path = 128
        ases = set([as_obj.asn])
        # Loop all the way through to the end
        for i in range(max_path + 1):
            # Get most specific announcement, or empty RIB
            most_specific_ann = self._get_most_specific_ann(as_obj, ordered_prefixes)
            if most_specific_ann is None:
                has_rib = False
                break
            elif most_specific_ann.recv_relationship == Relationships.ORIGIN:
                break
            else:
                # Continue looping by getting the last AS
                as_obj = self.engine.as_dict[most_specific_ann.as_path[1]]
                if as_obj.asn in ases:
                    print(ases)
                    input("looping")
                else:
                    ases.add(as_obj.asn)
                # If the attacker is on the path, the outcome is hijacked
                if as_obj.asn == self.attack.attacker_asn:
                    return as_obj, has_rib
        assert i != max_path, "looping"
        return as_obj, has_rib

    def _store_outcome(self, as_obj, has_rib, og_as_obj, outcomes):
        if has_rib:
            # Store the outcome so long as there is a rib
            if as_obj.asn == self.attack.attacker_asn:
                outcomes[Outcomes.HIJACKED][og_as_obj.policy.name] += 1
            elif as_obj.asn == self.attack.victim_asn:
                outcomes[Outcomes.NOT_HIJACKED][og_as_obj.policy.name] += 1
            else:
                outcomes[Outcomes.DISCONNECTED][og_as_obj.policy.name] += 1
        else:
            outcomes[Outcomes.DISCONNECTED][og_as_obj.policy.name] += 1

    def _get_ordered_prefixes(self):
        prefixes = set()
        for ann in self.attack.announcements:
            prefixes.add(ann.prefix)

        assert len(prefixes) > 0
        # Prefixes with most specific subprefix first
        return tuple(sorted(prefixes, key=lambda x: ipaddress.ip_network(x).num_addresses))

    def _get_most_specific_ann(self, as_obj, ordered_prefixes):
        for prefix in ordered_prefixes:
            most_specific_prefix = as_obj.policy.local_rib.get(prefix)
            if most_specific_prefix is not None:
                break
        return most_specific_prefix

    def _get_policy_totals(self, policy_names, subgraph_asns):
        """Determines the total amount of ASes per policy"""

        totals = {x: 0 for x in policy_names}
        for asn in subgraph_asns:
            if asn in [self.attack.attacker_asn, self.attack.victim_asn]:
                continue
            as_obj = self.engine.as_dict[asn]
            totals[as_obj.policy.name] += 1
        return totals
