"""Check readable Ward displays for large observation sets."""

from matplotlib.pyplot import close
from numpy import linspace
from polars import DataFrame

from src.services.visualization import plot_hierarchical_tree


def test_large_tree_aggregates_leaves_without_dropping_observations() -> None:
    observations = DataFrame({"value_pu": linspace(1.0, 2.0, 100)})
    figure, axis = plot_hierarchical_tree(observations)
    labels = [label.get_text() for label in axis.get_xticklabels()]
    represented_count = sum(
        int(label.strip("()")) if label.startswith("(") else 1
        for label in labels
    )
    assert len(labels) == 30
    assert represented_count == 100
    close(figure)
