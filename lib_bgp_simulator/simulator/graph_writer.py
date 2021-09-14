from collections import defaultdict
import math
import os
from statistics import mean, stdev

import matplotlib
import matplotlib.pyplot as plt

from ..enums import Outcomes

class Line:
    def __init__(self):
        self.x = []
        self.y = []
        self.yerr = []

def aggregate_and_write(self, graph_dir):
    """Writes the graph in specified dir"""

    for subgraph_name in self.subgraphs:
        for outcome in list(Outcomes):
            for propagation_round in range(self.propagation_rounds):
                adopting_lines = defaultdict(Line)
                non_adopting_lines = defaultdict(Line)
                for data_point, list_of_scenarios in self.data_points.items():
                    if data_point.propagation_round != propagation_round:
                        continue

                    # Get percentages for this outcome
                    percentages = defaultdict(list)
                    for scenario in list_of_scenarios:
                        # Returns {policy: int}
                        data = scenario.data["data"][subgraph_name][outcome]
                        # Returns {policy: total_num}
                        totals = scenario.data["totals"][subgraph_name]
                        for policy, num in data.items():
                            percentages[policy].append(num * 100 // totals[policy])

                    # Aggregate now into a line
                    for policy, list_of_percents in percentages.items():
                        line = None
                        if policy == data_point.PolicyCls.name:
                            line = adopting_lines[policy]
                        else:
                            line = non_adopting_lines[f"{policy} ({data_point.PolicyCls.name} adopting)"]
                        line.x.append(data_point.percent_adoption)
                        line.y.append(mean(list_of_percents))
                        # 95% conf intervals
                        # If trials == 1, stdev doesn't work
                        if len(list_of_percents) > 1:
                            line.yerr.append(1.645 * 2 * stdev(list_of_percents) / math.sqrt(len(list_of_percents)))
                        else:
                            line.yerr.append(0)
                # Write graph here
                self._write(adopting_lines, outcome, subgraph_name,
                            propagation_round, graph_dir, adopting=True)
                self._write(non_adopting_lines, outcome, subgraph_name,
                            propagation_round, graph_dir, adopting=False)

def _write(self, lines, outcome, subgraph_name, propagation_round, graph_dir, adopting=False):
    fig, ax = plt.subplots()
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    for policy, line in lines.items():
        #input()
        ax.errorbar(line.x, line.y, yerr=line.yerr, label=policy, marker="*")

    ax.set_ylabel(f"Percent {outcome.name}")
    ax.set_xlabel("Percent adoption of adopted policy")

    # Might throw warnings later?
    ax.legend()
    plt.tight_layout()
    plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
    matplotlib.use('Agg')
    fname = (f"{outcome.name}_round_{propagation_round}.png")
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    subgraph_dir = os.path.join(graph_dir, subgraph_name)
    if not os.path.exists(subgraph_dir):
        os.makedirs(subgraph_dir)
    atk_dir = os.path.join(subgraph_dir, self.AttackCls.__name__)
    if not os.path.exists(atk_dir):
        os.makedirs(atk_dir)
    adopting_dir = os.path.join(atk_dir, "adopting" if adopting else "non_adopting")
    if not os.path.exists(adopting_dir):
        os.makedirs(adopting_dir)
    plt.savefig(os.path.join(adopting_dir, fname))
