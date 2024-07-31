import gc
from statistics import mean

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

    first_legend, aggregated_labels_handles_dict = self._add_legend(
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
        aggregated_labels_handles_dict,
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

    # non aggregated
    non_aggregated_labels = set([x.label for x in non_aggregated_data_dict.values()])
    non_aggregated_labels_handles_dict = dict()
    aggregated_labels_handles_dict = dict()
    for handle, label in zip(handles, labels):
        # This is a placeholder line, don't plot in the legend
        if label == self.strongest_attacker_legend_label:
            continue
        elif label in non_aggregated_labels:
            non_aggregated_labels_handles_dict[label] = handle
        else:
            aggregated_labels_handles_dict[label] = handle

    mean_y_dict = {
        line_data.line_info.label: mean(line_data.ys)
        for label, line_data in non_aggregated_data_dict.items()
    }
    sorted_labels = [
        label for label in sorted(
            non_aggregated_labels_handles_dict,
            key=lambda label: mean_y_dict[label],
            reverse=True
        )
    ]
    sorted_handles = [non_aggregated_labels_handles_dict[lbl] for lbl in sorted_labels]

    first_legend = ax.legend(sorted_handles, sorted_labels)
    return first_legend, aggregated_labels_handles_dict


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
    aggregated_labels_handles_dict,
):
    """Add second legend for strongest attacker"""

    # Only run if there is a secondary strongest attacker
    if not self.strongest_attacker_labels:
        return

    ax.add_artist(first_legend)
    # First you must draw the legend so that you can get it's location
    plt.tight_layout()
    # https://stackoverflow.com/a/43748841/8903959
    fig.canvas.draw()

    bbox = first_legend.get_window_extent()
    # Transform the bounding box into figure coordinates
    bbox_transformed = bbox.transformed(fig.transFigure.inverted())

    ax.legend(
        handles=list(aggregated_labels_handles_dict.values()),
        title=self.strongest_attacker_legend_label,
        # Upper right corner should line up
        loc="upper right",
        bbox_to_anchor=(bbox_transformed.x1, bbox_transformed.y0),
        bbox_transform=fig.transFigure,
    )


def _save_and_close_graph(self, fig, ax, graph_name):
    """Saves and closes the graph"""

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
