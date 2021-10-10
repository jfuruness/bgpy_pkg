from collections import defaultdict
import math
import os
import shutil
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

    print("Can't do this with more than 1 graph, write a better solution")
    shutil.rmtree(graph_dir)
    for subgraph_name in self.subgraphs:
        for outcome in list(Outcomes):
            for propagation_round in range(self.propagation_rounds):
                all_ases_lines = defaultdict(Line)
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
                        agg_num = 0
                        total = 0
                        # For aggregate graph lol
                        #####################################################3
                        for subg_name in self.subgraphs:
                            data = scenario.data["data"][subg_name][outcome]
                            totals = scenario.data["totals"][subg_name]
                            for policy, num in data.items():
                                agg_num += num
                                total += totals[policy]
                        percentages["all_ases"].append(agg_num * 100 // total)

                    # Aggregate now into a line
                    for policy, list_of_percents in percentages.items():
                        line = None
                        if policy == data_point.ASCls.name:
                            line = adopting_lines[policy]
                        elif policy == "all_ases":
                            line = all_ases_lines[f"all_ases {data_point.ASCls.name}"]
                        else:
                            line = non_adopting_lines[f"{policy} ({data_point.ASCls.name} adopting)"]
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
                            propagation_round, graph_dir, adopting="adopting")
                self._write(non_adopting_lines, outcome, subgraph_name,
                            propagation_round, graph_dir, adopting="non_adopting")
                self._write(all_ases_lines, outcome, "ALL", propagation_round,
                            graph_dir, adopting="all")

def _write(self, lines, outcome, subgraph_name, propagation_round, graph_dir, adopting=None):
    fig, ax = plt.subplots()
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    for policy, line in lines.items():
        #input()
        ax.errorbar(line.x, line.y, yerr=line.yerr, label=policy, marker="*")

    ax.set_ylabel(self.AttackCls.y_labels[outcome])
    ax.set_xlabel("Percent adoption of adopted policy")

    # Might throw warnings later?
    #ax.legend()
    # I do this because of the stupid warning that occurs if I don't
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
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
    if adopting != "all":
        adopting_dir = os.path.join(atk_dir, adopting)
        if not os.path.exists(adopting_dir):
            os.makedirs(adopting_dir)
    else:
        adopting_dir = atk_dir
    plt.savefig(os.path.join(adopting_dir, fname))
    # Done here so that it does not leave graphs open which accumulate memory
    # Other methods appear to be wrong here
    # https://stackoverflow.com/a/33343289/8903959
    plt.close(fig)
