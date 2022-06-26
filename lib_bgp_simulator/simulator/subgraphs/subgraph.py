from abc import ABC, abstractmethod
from collections import defaultdict

from ...enums import ASTypes


class Subgraph(ABC):
    """A subgraph for data display"""

    __slots__ = ("data",)

    def __init__(self):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # {scenario_label: {percent_adopt: [percentages]}}
        self.data = defaultdict(lambda: defaultdict(list))

    def add_trial_info(self, other_subgraph):
        """Merges other subgraph into this one and combines the data"""

        for scenario_label, percent_dict in other_subgraph.data.items():
            for percent_adopt, trial_results in percent_dict.items():
                self.data[scenario_label][percent_adopt].extend(trial_results)

    def aggregate_engine_run_data(self,
                                  shared_data,
                                  engine,
                                  *,
                                  percent_adopt,
                                  trial,
                                  scenario,
                                  propagation_round):
        """Aggregates data after a single engine run

        Shared data is passed between subgraph classes and is
        mutable. This is done to speed up data aggregation, even
        though it is at the cost of immutability

        shared data is reset after every run

        shared_data ex:
        {stubs_hijacked: int,
         stubs_hijacked_total: int,
         stubs_hijacked_percentage: float,
         stubs_hijacked_adopting: int
         stubs_hijacked_adopting_total: int,
         stubs_hijacked_adopting_percentage: float,
         stubs_hijacked_non_adopting: int,
         stubs_hijacked_non_adopting_total: int
         stubs_hijacked_non_adopting_percentage: float,
         ...
         }

        self.data ex:
        {scenario_label: {percent_adopt: [percents]}}
        """

        if not shared.get("set"):
            self._add_traceback_to_shared_data(shared_data, engine, scenario)
        key = self._get_subgraph_key(scenario)
        self.data[scenario.__class__.__name__][percent_adopt].append(
            shared_data[key])

    @abstractmethod
    def _get_subgraph_key(self, scenario):
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError

#####################
# Shared data funcs #
#####################

    def _add_traceback_to_shared_data(self, shared, engine, scenario):
        """Adds traceback info to shared data"""

        # {as_obj: outcome}
        outcomes = self._get_engine_outcomes(engine, scenario)
        for as_obj, outcome in outcomes.items():
            as_type = self._get_as_type(as_obj) 

            # TODO: refactor this ridiculousness into a class
            # Add to the AS type and policy, as well as the outcome
            as_type_pol_k = self._get_as_type_pol_k(as_type, as_obj.name)
            as_type_pol_outcome_k = self._get_as_type_pol_outcome_k(
                as_type, as_obj.name, outcome)
            # as type + policy + outcome as a percentage
            as_type_pol_outcome_perc_k = self._get_as_type_pol_outcome_perc_k(
                as_type, as_obj.name, outcome)
            # Add to the totals:
            for k in [as_type_pol_k, as_type_pol_outcome_k]:
                shared[k] = shared.get(k, 0) + 1
            # Set the new percent
            shared[as_type_pol_outcome_perc_k] = (shared[as_type_pol_outcome_k]
                                                  / shared[as_type_pol_k])
        shared["set"] = True


    def _get_as_type(self, as_obj):
        """Returns the type of AS (stub_or_mh, input_clique, or etc)"""

        if as_obj.stub or as_obj.multihomed:
            return ASTypes.STUBS_OR_MH
        elif as_obj.input_clique:
            return ASTypes.INPUT_CLIQUE
        else:
            return ASTypes.ETC

    def _get_as_type_pol_k(self, as_type, policy_name):
        """Returns AS type+policy key"""

        return f"{as_type.value}_{policy_name}"

    def _get_as_type_pol_outcome_k(self,
                                   as_type,
                                   pol_name,
                                   outcome):
        """returns as type+policy+outcome key"""

        return f"{self._get_as_type_pol_k(as_type, pol_name)}_{outcome.name}"

    def _get_as_type_pol_outcome_perc_k(self,
                                        as_type,
                                        pol_name,
                                        outcome):
        """returns as type+policy+outcome key as a percent"""

        x = self._get_as_type_pol_outcome_k(as_type, pol_name, outcome)
        return f"{x}_percent"

###################
# Traceback funcs #
###################

    def _get_engine_outcomes(self, engine, scenario):
        """Gets the outcomes of all ASes"""

        # {ASN: outcome}
        outcomes = dict()
        for as_obj in engine.as_dict.values():
            # Gets AS outcome and stores it in the outcomes dict
            self._get_as_outcome(as_obj,
                                 outcomes,
                                 engine,
                                 scenario)
        return outcomes

    def _get_as_outcome(self, as_obj, outcomes, engine, scenario):
        """Returns the as outcome"""

        if as_obj in outcomes:
            return outcomes[as_obj]
        else:
            # Get the most specific announcement in the rib
            most_specific_ann = self._get_most_specific_ann(
                as_obj, scenario.ordered_prefix_subprefix_dict)
            # This has to be done in the scenario
            # Because only the scenario knows attacker/victim
            # And it's possible for scenario's to have multiple attackers
            # or multiple victims or different ways of determining outcomes
            outcome = scenario._determine_outcome(as_obj, most_specific_ann)
            # We haven't traced back all the way on the AS path
            if outcome == Outcomes.UNDETERMINED:
                # next as in the AS path to traceback to
                next_as = engine.as_dict[most_specific_ann.as_path[1]]
                outcome = self._get_as_outcome(next_as,
                                               outcomes,
                                               scenario)
            assert outcome != Outcomes.UNDETERMINED, "Shouldn't be possible"

            outcomes[as_obj] = outcome
            return outcome
            
    def _get_most_specific_ann(self, as_obj, ordered_prefixes):
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        for prefix in ordered_prefixes:
            most_specific_ann = as_obj._local_rib.get_ann(prefix)
            if most_specific_ann:
                return most_specific_ann
