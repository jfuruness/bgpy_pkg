import gc
from statistics import mean

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt  # type: ignore


def _add_legends_and_save(
    self,
    fig,
    ax,
    metric_key,
    relevant_rows,
    adopting,
    non_aggregated_data_dict,
    max_attacker_dict,
    graph_name,
):

    first_legend = self._add_legend(
        fig,
        ax,
        metric_key,
        relevant_rows,
        adopting,
        non_aggregated_data_dict,
        max_attacker_dict,
    )

    self._add_strongest_attacker_legend(
        fig,
        ax,
        metric_key,
        relevant_rows,
        adopting,
        non_aggregated_data_dict,
        max_attacker_dict,
        first_legend,
    )

    self._save_and_close_graph(fig, ax, graph_name)


def _add_legend(
    self,
    fig,
    ax,
    metric_key,
    relevant_rows,
    adopting,
    non_aggregated_data_dict,
    max_attacker_data_dict,
):
    """Add legend to the graph"""

    # This is to avoid warnings
    handles, labels = ax.get_legend_handles_labels()
    labels_handles_dict = {label: handle for label, handle in zip(labels, handles)}
    mean_y_dict = {
        line_data.line_info.label: mean(line_data.ys)
        for label, line_data in non_aggregated_data_dict.items()
    }
    sorted_labels = [
        x[1] for x in sorted(
            zip(handles, labels),
            key=lambda x: mean_y_dict[x[1]],
            reverse=True
        )
    ]
    sorted_handles = [labels_handles_dict[label] for label in sorted_labels]

    return ax.legend(sorted_handles, sorted_labels)


def _add_strongest_attacker_legend(
    self,
    fig,
    ax,
    metric_key,
    relevant_rows,
    adopting,
    non_aggregated_data_dict,
    max_attacker_data_dict,
    first_legend,
):
    """Add second legend for strongest attacker"""

    # Only run if there is a secondary strongest attacker
    if not self.strongest_attacker_labels:
        return

    legend_elements = list()
    for label, line_data in max_attacker_data_dict.items():
        legend_elements.append(
            mpatches.Patch(
                color=line_data.line_info.color,
                marker=line_data.line_info.marker,
                label=line_data.label,
            )
        )

    # https://riptutorial.com/matplotlib/example/32429/multiple-legends-on-the-same-axes
    # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    ax.legend(handles=legend_elements)
    ax.add_artist(first_legend)


def _save_and_close_graph(self, fig, ax, graph_name):
    """Saves and closes the graph"""

    plt.tight_layout()

    path = self.graph_dir / graph_name
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path)
    # https://stackoverflow.com/a/33343289/8903959
    ax.cla()
    plt.cla()
    plt.clf()
    # If you just close the fig, on machines with many CPUs and trials,
    # there is some sort of a memory leak that occurs. See stackoverflow
    # comment above
    plt.close(fig)
    # If you are running one simulation after the other, matplotlib
    # basically leaks memory. I couldn't find the original issue, but
    # here is a note in one of their releases saying to just call the garbage
    # collector: https://matplotlib.org/stable/users/prev_whats_new/
    # whats_new_3.6.0.html#garbage-collection-is-no-longer-run-on-figure-close
    # and here is the stackoverflow post on this topic:
    # https://stackoverflow.com/a/33343289/8903959
    # Even if this works without garbage collection in 3.5.2, that will break
    # as soon as we upgrade to the latest matplotlib which no longer does
    # If you run the simulations on a machine with many cores and lots of trials,
    # this bug leaks enough memory to crash the server, so we must garbage collect
    gc.collect()
