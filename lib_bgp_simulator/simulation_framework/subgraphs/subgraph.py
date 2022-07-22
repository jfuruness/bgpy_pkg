from abc import ABC
from collections import defaultdict
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt

from .line import Line
from ...enums import ASTypes
from ...enums import Outcomes
from ...simulation_engine import SimulationEngine
from ..scenarios import Scenario
from ...simulation_engine.announcement import Announcement as Ann


from lib_caida_collector import AS

# Must be module level in order to be picklable
# https://stackoverflow.com/a/16439720/8903959
def default_dict_func() -> defaultdict:
    return defaultdict(list)


class Subgraph(ABC):
    """A subgraph for data display"""

    __slots__ = ("data",)  # type: ignore

    name: Optional[str] = None

    subclasses: list = []

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to know all attackers that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        cls.subclasses.append(cls)
        names: list = [x.name for x in cls.subclasses if x.name]
        assert len(set(names)) == len(names), "Duplicate subgraph class names"

    def __init__(self):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # {scenario_label: {percent_adopt: [percentages]}}
        self.data: defaultdict = defaultdict(default_dict_func)

###############
# Graph funcs #
###############

    def write_graph(self, graph_dir):
        """Writes graph into the graph directory"""

        lines: list = self._get_lines()

        matplotlib.use("Agg")
        fig, ax = plt.subplots()
        # Set X and Y axis size
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        # Add the data from the lines
        for line in lines:
            ax.errorbar(line.xs,
                        line.ys,
                        yerr=line.yerrs,
                        label=line.label)
        # Set labels
        ax.set_ylabel(self.y_axis_label)
        ax.set_xlabel(self.x_axis_label)

        # This is to avoid warnings
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        plt.tight_layout()
        plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
        plt.savefig(graph_dir / f"{self.name}.png")
        # https://stackoverflow.com/a/33343289/8903959
        plt.close(fig)

    def _get_lines(self) -> list:
        """Returns lines for matplotlib graph"""

        return [Line(k, v) for k, v in self.data.items()]

    @property
    def y_axis_label(self):
        """returns y axis label"""

        raise NotImplementedError

    @property
    def x_axis_label(self) -> str:
        """Returns X axis label"""

        return "Percent adoption of the adopted class"

##############
# Data funcs #
##############

    def add_trial_info(self, other_subgraph: "Subgraph"):
        """Merges other subgraph into this one and combines the data"""

        for scenario_label, percent_dict in other_subgraph.data.items():
            for percent_adopt, trial_results in percent_dict.items():
                self.data[scenario_label][percent_adopt].extend(trial_results)

    def aggregate_engine_run_data(self,
                                  shared_data: dict,
                                  engine: SimulationEngine,
                                  *,
                                  percent_adopt: float,
                                  trial,
                                  scenario: Scenario,
                                  propagation_round: int):
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

        if not shared_data.get("set"):
            # {as_obj: outcome}
            outcomes = self._get_engine_outcomes(engine, scenario)
            self._add_traceback_to_shared_data(shared_data,
                                               engine,
                                               scenario,
                                               outcomes)
        key = self._get_subgraph_key(scenario)
        self.data[scenario.graph_label][percent_adopt].append(
            shared_data.get(key, 0))

    def _get_subgraph_key(self, scenario):
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError

#####################
# Shared data funcs #
#####################

    def _add_traceback_to_shared_data(self,
                                      shared: dict,
                                      engine: SimulationEngine,
                                      scenario: Scenario,
                                      outcomes: dict):
        """Adds traceback info to shared data"""

        for as_obj, outcome in outcomes.items():
            as_type = self._get_as_type(as_obj)

            # TODO: refactor this ridiculousness into a class
            # Add to the AS type and policy, as well as the outcome
            as_type_pol_k = self._get_as_type_pol_k(as_type, as_obj.__class__)
            as_type_pol_outcome_k = self._get_as_type_pol_outcome_k(
                as_type, as_obj.__class__, outcome)
            # as type + policy + outcome as a percentage
            as_type_pol_outcome_perc_k = self._get_as_type_pol_outcome_perc_k(
                as_type, as_obj.__class__, outcome)
            # Add to the totals:
            for k in [as_type_pol_k, as_type_pol_outcome_k]:
                shared[k] = shared.get(k, 0) + 1
            # Set the new percent
            shared[as_type_pol_outcome_perc_k] = (
                shared[as_type_pol_outcome_k] * 100 / shared[as_type_pol_k])

        shared["set"] = True

    def _get_as_type(self, as_obj: AS) -> ASTypes:
        """Returns the type of AS (stub_or_mh, input_clique, or etc)"""

        if as_obj.stub or as_obj.multihomed:
            return ASTypes.STUBS_OR_MH
        elif as_obj.input_clique:
            return ASTypes.INPUT_CLIQUE
        else:
            return ASTypes.ETC

    def _get_as_type_pol_k(self, as_type: ASTypes, ASCls: AS) -> str:
        """Returns AS type+policy key"""

        return f"{as_type.value}_{ASCls.name}"

    def _get_as_type_pol_outcome_k(self,
                                   as_type: ASTypes,
                                   ASCls: AS,
                                   outcome: Outcomes) -> str:
        """returns as type+policy+outcome key"""

        return f"{self._get_as_type_pol_k(as_type, ASCls)}_{outcome.name}"

    def _get_as_type_pol_outcome_perc_k(self,
                                        as_type: ASTypes,
                                        ASCls: AS,
                                        outcome: Outcomes) -> str:
        """returns as type+policy+outcome key as a percent"""

        x = self._get_as_type_pol_outcome_k(as_type, ASCls, outcome)
        return f"{x}_percent"

###################
# Traceback funcs #
###################

    def _get_engine_outcomes(self, engine: SimulationEngine, scenario: Scenario) -> dict[int, Optional[Outcomes]]:
        """Gets the outcomes of all ASes"""

        # {ASN: outcome}
        outcomes: dict[int, Optional[Outcomes]] = dict()
        for as_obj in engine.as_dict.values():
            # Gets AS outcome and stores it in the outcomes dict
            self._get_as_outcome(as_obj,
                                 outcomes,
                                 engine,
                                 scenario)
        return outcomes

    def _get_as_outcome(self, as_obj: AS,
                        outcomes: dict[int, Optional[Outcomes]],
                        engine: SimulationEngine,
                        scenario: Scenario) -> Optional[Outcomes]:
        """Recursively returns the as outcome"""

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
            outcome = scenario.determine_as_outcome(as_obj, most_specific_ann)
            # We haven't traced back all the way on the AS path
            if outcome == Outcomes.UNDETERMINED:
                # next as in the AS path to traceback to
                next_as = engine.as_dict[most_specific_ann.as_path[1]]  # type: ignore
                outcome = self._get_as_outcome(next_as,
                                               outcomes,
                                               engine,
                                               scenario)
            assert outcome != Outcomes.UNDETERMINED, "Shouldn't be possible"

            outcomes[as_obj] = outcome
            return outcome

    def _get_most_specific_ann(self, as_obj: AS, ordered_prefixes: dict) -> Optional[Ann]:
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        for prefix in ordered_prefixes:
            most_specific_ann = as_obj._local_rib.get_ann(prefix)
            if most_specific_ann:
                return most_specific_ann
        return None
