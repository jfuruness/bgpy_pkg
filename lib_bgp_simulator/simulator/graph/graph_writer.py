import math
from statistics import mean, stdev
import sys

from lib_utils.helper_funcs import mp_call

from .line import Line

from ...enums import Outcomes

try:
    import matplotlib
    import matplotlib.pyplot as plt
except Exception as e:
    print(e, "Catch this specific exception in graph_writer later")


def aggregate_and_write(self, graph_dir, sim):
    """Writes the graph in specified dir"""

    all_lines_to_write = []
    all_outcomes = []
    all_subg_names = []
    all_propagation_rounds = []
    all_adopting = []

    for subg_name, outcome, propagation_round in self.get_graphs_to_write():
        # {policy: Line}
        lines = dict()

        for data_point, list_of_scenarios in self.data_points.items():
            if data_point.propagation_round != propagation_round:
                continue

            policies = list_of_scenarios[0].outcome_policy_percentages[
                subg_name][outcome].keys()
            for policy in policies:
                line = self._get_line(policy, lines, data_point)
                line.add_data(data_point.percent_adoption,
                              list_of_scenarios,
                              subg_name,
                              outcome,
                              policy)

        adopting_lines = [x for x in lines.values() if x.adopting]
        non_adopting_lines = [x for x in lines.values() if not x.adopting]

        for lines_to_write, adopting in [[adopting_lines, True],
                                         [non_adopting_lines, False]]:
            all_lines_to_write.append(lines_to_write)
            all_outcomes.append(outcome)
            all_subg_names.append(subg_name)
            all_propagation_rounds.append(propagation_round)
            all_adopting.append(adopting)

    all_args = [all_lines_to_write,
                all_outcomes,
                all_subg_names,
                all_propagation_rounds,
                all_adopting]
    mp_call(self._write, all_args, desc="Writing graphs")


def get_graphs_to_write(self):
    for subgraph_name in self.subgraphs:
        for outcome in list(Outcomes):
            for propagation_round in range(self.propagation_rounds):
                yield subgraph_name, outcome, propagation_round


def _get_line(self, policy, lines, data_point):
    if policy == data_point.ASCls.name:
        label = policy
        adopting = True
    else:
        label = f"{policy} ({data_point.ASCls.name} adopting"
        adopting = False
    if lines.get(label) is None:
        lines[label] = Line(policy, adopting, label)

    return lines[label]


def _write(self, lines, outcome, subg_name, propagation_round, adopting):
    fig, ax = plt.subplots()
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    for line in lines:
        ax.errorbar(line.x,
                    line.y,
                    yerr=line.yerr,
                    label=line.label,
                    marker="*")

    ax.set_ylabel(self.EngineInputCls.y_labels[outcome])
    ax.set_xlabel("Percent adoption of adopted policy")

    # I do this because of the stupid warning that occurs if I don't
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    plt.tight_layout()
    plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
    matplotlib.use('Agg')
    fname = f"{outcome.name}_round_{propagation_round}.png"

    adopting_name = "adopting" if adopting else "non adopting"
    final_dir = self._dir / subg_name / self.EngineInputCls.__name__ / adopting_name
    final_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(final_dir / fname)
    # Done here so that it does not leave graphs open which accumulate memory
    # Other methods appear to be wrong here
    # https://stackoverflow.com/a/33343289/8903959
    plt.close(fig)
