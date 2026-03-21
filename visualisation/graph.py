from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, Sequence, runtime_checkable

import matplotlib.pyplot as plt
import numpy as np


@runtime_checkable
class SnapshotSeries(Protocol):
    """Minimal protocol for plottable snapshot histories."""

    title: str
    snapshots: Sequence[Mapping[str, Any]]


@dataclass(frozen=True)
class CitySnapshotSeries:
    """Adapter exposing a city's stored snapshots through the graph protocol."""

    city: Any

    @property
    def title(self) -> str:
        return self.city.name

    @property
    def snapshots(self) -> Sequence[Mapping[str, Any]]:
        return self.city.city_data.data


def extract_snapshot_values(
    snapshots: Sequence[Mapping[str, Any]],
    y_getter: Callable[[Mapping[str, Any]], float | int],
) -> np.ndarray:
    """Extract y-values from ordered snapshots as a NumPy array."""

    return np.array([y_getter(snapshot) for snapshot in snapshots])


def plot_snapshot_series(
    series: SnapshotSeries | Sequence[Mapping[str, Any]],
    y_getter: Callable[[Mapping[str, Any]], float | int],
    *,
    title: str | None = None,
    xlabel: str = "Week",
    ylabel: str = "Value",
) -> None:
    """Plot a time series by extracting y-values from stored snapshots."""

    snapshots = series.snapshots if isinstance(series, SnapshotSeries) else series
    ypoints = extract_snapshot_values(snapshots, y_getter)

    plt.plot(ypoints)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title or getattr(series, "title", "Time series"))
    plt.show()


def graph_total_pop(city):
    """Plot the total population of a city over time."""

    plot_snapshot_series(
        CitySnapshotSeries(city),
        lambda snapshot: snapshot["city_data"]["population"],
        ylabel="Population",
    )
