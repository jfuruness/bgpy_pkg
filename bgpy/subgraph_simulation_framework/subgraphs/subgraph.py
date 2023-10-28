from abc import ABC
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Type, Union

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from .line import Line
from bgpy.enums import ASGroups
from bgpy.enums import Outcomes
from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import SimulationEngine
from bgpy.simulation_framework.scenarios import Scenario
from bgpy.simulation_engine.announcement import Announcement as Ann

from bgpy.caida_collector import AS


# Must be module level in order to be picklable
# https://stackoverflow.com/a/16439720/8903959
def default_dict_inner_func():
    return defaultdict(list)


def default_dict_func():
    return defaultdict(default_dict_inner_func)


class Subgraph(ABC):
    """A subgraph for data display"""

    __slots__ = ("data",)  # type: ignore

    name: Optional[str] = None

    subclasses: List[Type["Subgraph"]] = []

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to know all attackers that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        cls.subclasses.append(cls)
        names = [x.name for x in cls.subclasses if x.name]
        assert len(set(names)) == len(names), "Duplicate subgraph class names"

    def __init__(self):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # {propagation_round: {scenario_label: {percent_adopt: [percentages]}}}
        self.data: DefaultDict[
            int,
            DefaultDict[
                str, DefaultDict[Union[float, SpecialPercentAdoptions], List[float]]
            ],
        ] = defaultdict(default_dict_func)

    ###############
    # Graph funcs #
    ###############

    def write_graphs(self, graph_dir: Path):
        """Writes all graphs into the graph dir"""

        for prop_round in self.data:
            self.write_graph(prop_round, graph_dir)

    def write_graph(self, prop_round: int, graph_dir: Path):
        """Writes graph into the graph directory"""

        lines: List[Line] = self._get_lines(prop_round)

        matplotlib.use("Agg")
        fig, ax = plt.subplots()
        fig.set_dpi(150)
        # Set X and Y axis size
        plt.xlim(0, 100)
        plt.ylim(0, 100)

        styles = self.line_styles
        markers = self.markers
        # Add the data from the lines
        for i, line in enumerate(sorted(lines, key=lambda x: x.label)):
            # Ya, not great I know.
            # Sorry, they don't pay me enough
            # In fact, they don't pay me at all
            assert self.name, "looking at you mypy"
            if "non_adopting" in self.name:
                adopt_pol = line.label.replace("adopting", "non-adopting")
                line.label = adopt_pol

            ax.errorbar(
                line.xs,
                line.ys,
                ls=styles[i],
                marker=markers[i],
                yerr=line.yerrs,
                label=line.label,
            )
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

    @property
    def markers(self) -> List[str]:
        markers = [".", "1", "*", "x", "d", "2", "3", "4"]
        markers += markers.copy()[0:-2:2]
        markers += markers.copy()[::-1]
        return markers

    @property
    def line_styles(self) -> List[str]:
        styles = ["-", "--", "-.", ":", "solid", "dotted", "dashdot", "dashed"]
        styles += styles.copy()[::-1]
        styles += styles.copy()[0:-2:2]
        return styles

    def _get_lines(self, prop_round: int) -> List[Line]:
        """Returns lines for matplotlib graph"""

        return [Line(k, v) for k, v in self.data[prop_round].items()]

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        raise NotImplementedError

    @property
    def x_axis_label(self) -> str:
        """Returns X axis label"""

        # Upon request from Cameron
        return "Percent Adoption"  # of the adopted class"

    ##############
    # Data funcs #
    ##############

    def add_trial_info(self, other_subgraph: "Subgraph"):
        """Merges other subgraph into this one and combines the data

        This gets called when we need to merge all the subgraphs
        from the various processes that were spawned
        """

        for prop_round, scenario_dict in other_subgraph.data.items():
            for scenario_label, percent_dict in scenario_dict.items():
                for percent_adopt, trial_results in percent_dict.items():
                    if isinstance(percent_adopt, SpecialPercentAdoptions):
                        percent_adopt = percent_adopt.value
                    self.data[prop_round][scenario_label][percent_adopt].extend(
                        trial_results
                    )  # noqa

    def aggregate_engine_run_data(
        self,
        shared_data: Dict[Any, Any],
        *,
        engine: SimulationEngine,
        percent_adopt: float,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
    ):
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
            self._add_traceback_to_shared_data(shared_data, engine, scenario, outcomes)
        key = self._get_subgraph_key(scenario)
        if isinstance(percent_adopt, SpecialPercentAdoptions):
            percent_adopt = percent_adopt.value
        self.data[propagation_round][scenario.graph_label][percent_adopt].append(
            shared_data.get(key, 0)
        )  # noqa

    def _get_subgraph_key(self, scenario: Scenario, *args: Any) -> str:
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError

    #####################
    # Shared data funcs #
    #####################

    def _add_traceback_to_shared_data(
        self,
        shared: Dict[Any, Any],
        engine: SimulationEngine,
        scenario: Scenario,
        outcomes: Dict[AS, Outcomes],
    ):
        """Adds traceback info to shared data"""

        # Do not count these!
        uncountable_asns = scenario._preset_asns

        for as_obj, outcome in outcomes.items():
            if as_obj.asn in uncountable_asns:
                continue

            as_type = self._get_as_type(as_obj)

            # TODO: refactor this ridiculousness into a class
            # Add to the AS type and policy, as well as the outcome

            # THESE ARE JUST KEYS, JUST GETTING KEYS/Strings HERE
            ##################################################################
            as_type_pol_k = self._get_as_type_pol_k(as_type, as_obj.__class__)
            as_type_pol_outcome_k = self._get_as_type_pol_outcome_k(
                as_type, as_obj.__class__, outcome
            )
            # as type + policy + outcome as a percentage
            as_type_pol_outcome_perc_k = self._get_as_type_pol_outcome_perc_k(
                as_type, as_obj.__class__, outcome
            )
            ##################################################################

            # Getting control plane data #
            # Get the most specific announcement in the rib
            most_specific_ann = self._get_most_specific_ann(
                as_obj, scenario.ordered_prefix_subprefix_dict
            )

            ctrl_outcome = scenario.determine_as_outcome(as_obj, most_specific_ann)
            as_type_pol_k_ctrl = as_type_pol_k + "_ctrl"
            as_type_pol_outcome_k_ctrl = (
                self._get_as_type_pol_outcome_k(as_type, as_obj.__class__, ctrl_outcome)
                + "_ctrl"
            )
            as_type_pol_outcome_perc_k_ctrl = (
                self._get_as_type_pol_outcome_perc_k(
                    as_type, as_obj.__class__, ctrl_outcome
                )
                + "_ctrl"
            )

            ###################################

            # Add to the totals:
            for k in [
                as_type_pol_k,
                as_type_pol_outcome_k,
                as_type_pol_k_ctrl,
                as_type_pol_outcome_k_ctrl,
            ]:
                shared[k] = shared.get(k, 0) + 1

            ############################
            # Track stats for all ASes #
            ############################

            # Keep track of totals for all ASes
            name = outcome.name
            total = shared.get(f"all_{name}", 0) + 1
            shared[f"all_{name}"] = total

        # Must calculate percentages at the end
        # NOTE: this double for loop should realy be avoided
        # Only O(2n) but bad for runtime
        for as_obj, outcome in outcomes.items():
            if as_obj.asn in uncountable_asns:
                continue

            as_type = self._get_as_type(as_obj)
            as_type_pol_k = self._get_as_type_pol_k(as_type, as_obj.__class__)
            as_type_pol_outcome_k = self._get_as_type_pol_outcome_k(
                as_type, as_obj.__class__, outcome
            )
            # as type + policy + outcome as a percentage
            as_type_pol_outcome_perc_k = self._get_as_type_pol_outcome_perc_k(
                as_type, as_obj.__class__, outcome
            )

            # Set the new percent
            if shared.get(as_type_pol_outcome_k) is not None:
                shared[as_type_pol_outcome_perc_k] = (
                    shared[as_type_pol_outcome_k] * 100 / shared[as_type_pol_k]
                )
            name = outcome.name
            total = shared[f"all_{name}"]
            # Keep track of percentages for all ASes
            shared[f"all_{name}_perc"] = total * 100 / len(outcomes)

            # Getting control plane data #
            # Get the most specific announcement in the rib
            most_specific_ann = self._get_most_specific_ann(
                as_obj, scenario.ordered_prefix_subprefix_dict
            )

            ctrl_outcome = scenario.determine_as_outcome(as_obj, most_specific_ann)
            as_type_pol_k_ctrl = as_type_pol_k + "_ctrl"
            as_type_pol_outcome_k_ctrl = (
                self._get_as_type_pol_outcome_k(as_type, as_obj.__class__, ctrl_outcome)
                + "_ctrl"
            )
            as_type_pol_outcome_perc_k_ctrl = (
                self._get_as_type_pol_outcome_perc_k(
                    as_type, as_obj.__class__, ctrl_outcome
                )
                + "_ctrl"
            )

            # Set the new percent
            if shared.get(as_type_pol_outcome_k_ctrl) is not None:
                shared[as_type_pol_outcome_perc_k_ctrl] = (
                    shared[as_type_pol_outcome_k_ctrl]
                    * 100
                    / shared[as_type_pol_k_ctrl]
                )

            ###################################

        shared["set"] = True

    def _get_as_type(self, as_obj: AS) -> ASGroups:
        """Returns the type of AS (stub_or_mh, input_clique, or etc)"""

        if as_obj.stub or as_obj.multihomed:
            return ASGroups.STUBS_OR_MH
        elif as_obj.input_clique:
            return ASGroups.INPUT_CLIQUE
        else:
            return ASGroups.ETC

    def _get_as_type_pol_k(self, as_type: ASGroups, ASCls: Type[AS]) -> str:
        """Returns AS type+policy key"""

        return f"{as_type.value}_{ASCls.name}"

    def _get_as_type_pol_outcome_k(
        self, as_type: ASGroups, ASCls: Type[AS], outcome: Outcomes
    ) -> str:
        """returns as type+policy+outcome key"""

        return f"{self._get_as_type_pol_k(as_type, ASCls)}_{outcome.name}"

    def _get_as_type_pol_outcome_perc_k(
        self, as_type: ASGroups, ASCls: Type[AS], outcome: Outcomes
    ) -> str:
        """returns as type+policy+outcome key as a percent"""

        x = self._get_as_type_pol_outcome_k(as_type, ASCls, outcome)
        return f"{x}_percent"

    ###################
    # Traceback funcs #
    ###################

    def _get_engine_outcomes(
        self, engine: SimulationEngine, scenario: Scenario
    ) -> Dict[AS, Outcomes]:
        """Gets the outcomes of all ASes"""

        # {ASN: outcome}
        outcomes: Dict[AS, Outcomes] = dict()
        for as_obj in engine.as_dict.values():
            # Gets AS outcome and stores it in the outcomes dict
            self._get_as_outcome(as_obj, outcomes, engine, scenario)
        return outcomes

    def _get_as_outcome(
        self,
        as_obj: AS,
        outcomes: Dict[AS, Outcomes],
        engine: SimulationEngine,
        scenario: Scenario,
    ) -> Outcomes:
        """Recursively returns the as outcome"""

        if as_obj in outcomes:
            return outcomes[as_obj]
        else:
            # Get the most specific announcement in the rib
            most_specific_ann = self._get_most_specific_ann(
                as_obj, scenario.ordered_prefix_subprefix_dict
            )
            # This has to be done in the scenario
            # Because only the scenario knows attacker/victim
            # And it's possible for scenario's to have multiple attackers
            # or multiple victims or different ways of determining outcomes
            outcome = scenario.determine_as_outcome(as_obj, most_specific_ann)
            # We haven't traced back all the way on the AS path
            if outcome == Outcomes.UNDETERMINED:
                # next as in the AS path to traceback to
                # Ignore type because only way for this to be here
                # Is if the most specific Ann was NOT None.
                next_as = engine.as_dict[
                    most_specific_ann.as_path[1]  # type: ignore
                ]  # type: ignore
                outcome = self._get_as_outcome(next_as, outcomes, engine, scenario)
            assert outcome != Outcomes.UNDETERMINED, "Shouldn't be possible"

            outcomes[as_obj] = outcome
            assert isinstance(outcome, Outcomes), "For mypy"
            return outcome

    def _get_most_specific_ann(
        self, as_obj: AS, ordered_prefixes: Dict[str, List[str]]
    ) -> Optional[Ann]:
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        for prefix in ordered_prefixes:
            most_specific_ann = as_obj._local_rib.get_ann(prefix)
            if most_specific_ann:
                # Mypy doesn't recognize that this is always an annoucnement
                return most_specific_ann  # type: ignore
        return None
