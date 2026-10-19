"""Compare fitted peak distributions in terminal-by-phase density panels."""

from warnings import catch_warnings, simplefilter

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.pyplot import subplots
from numpy import isfinite, linspace, ptp
from polars import DataFrame, col
from scipy.stats import FitError, gamma, lognorm, norm

MODELS = {"normal": norm, "gamma": gamma, "lognormal": lognorm}
SCOPE = ["scenario", "sample_size", "source_lineage", "terminal", "phase"]


def compare_distributions(observations: DataFrame) -> DataFrame:
    """Fit normal, gamma and lognormal by maximum likelihood per scope.

    Location is estimated for all families; normal has two free parameters,
    gamma and lognormal have three. AIC ranks relative fit, not adequacy.
    Failed, constant, undersized or non-finite groups remain explicit.

    Returns:
        Three rows per group with parameters, log likelihood and AIC.
    """
    rows: list[dict[str, str | int | float | bool | None]] = []
    for group in observations.partition_by(SCOPE, maintain_order=True):
        values = group["value_pu"].to_numpy()
        scope = {name: group.item(0, name) for name in SCOPE}
        for name, model in MODELS.items():
            count = 2 if name == "normal" else 3
            row = {
                **scope,
                "model": name,
                "n": len(values),
                "parameter_count": count,
                "location_policy": "estimated",
                "method": "MLE",
                "shape": None,
                "location": None,
                "scale": None,
                "log_likelihood": None,
                "aic": None,
                "status": "unavailable",
                "reason": "",
                "selected": False,
            }
            if len(values) < 4 or not isfinite(values).all():
                row["reason"] = "At least four finite peaks required."
            elif ptp(values) == 0:
                row["reason"] = "Constant observations."
            else:
                try:
                    with catch_warnings(record=True) as notices:
                        simplefilter("always", RuntimeWarning)
                        parameters = tuple(float(p) for p in model.fit(values))
                        likelihood = float(
                            model.logpdf(values, *parameters).sum()
                        )
                    if not isfinite(parameters).all() or not isfinite(
                        likelihood
                    ):
                        raise ValueError(
                            "Non-finite fitted parameters or likelihood."
                        )
                    if parameters[-1] <= 0:
                        raise ValueError("Non-positive fitted scale.")
                    row.update(
                        shape=parameters[0] if count == 3 else None,
                        location=parameters[-2],
                        scale=parameters[-1],
                        log_likelihood=likelihood,
                        aic=2 * count - 2 * likelihood,
                        status="fitted",
                        reason="; ".join(
                            str(item.message) for item in notices
                        ),
                    )
                except (
                    ValueError,
                    RuntimeError,
                    FitError,
                    FloatingPointError,
                ) as error:
                    row["reason"] = str(error)
            rows.append(row)
        fitted = [row for row in rows[-3:] if row["status"] == "fitted"]
        if fitted:
            best = min(fitted, key=lambda row: float(str(row["aic"])))
            best["selected"] = True
    return DataFrame(rows, infer_schema_length=None)


def plot_distribution_histograms(
    observations: DataFrame,
    comparison: DataFrame,
    terminals: tuple[str, ...],
) -> tuple[Figure, tuple[Axes, ...]]:
    """Plot density panels with normal and lowest-AIC model overlays.

    Each panel uses 20 equal-width bins over its own observed range. Every
    valid peak contributes; fitted curves never alter histogram counts.
    Annotations report observed mean and standard deviation (ddof=0) in p.u.

    Returns:
        Figure and axes ordered by terminal row and phase column.

    Raises:
        ValueError: If input is empty or mixes source scopes.
    """
    identity = ["scenario", "sample_size", "source_lineage"]
    if (
        observations.is_empty()
        or observations.select(identity).unique().height != 1
    ):
        raise ValueError("Density panels require one nonempty source scope.")
    phases = ("A", "B", "C")
    figure, grid = subplots(
        len(terminals),
        3,
        figsize=(15, 3.6 * len(terminals)),
        squeeze=False,
        sharex=True,
        sharey=True,
    )
    names = {
        "T_MAN": "Switching terminal",
        "1_2LT": "Line midpoint",
        "T_OPO": "Opposite terminal",
    }
    values = observations["value_pu"].to_numpy()
    padding = max(float(ptp(values)) * 0.08, 0.02)
    left, right = float(values.min()) - padding, float(values.max()) + padding
    x_values = linspace(left, right, 1200)
    for row_index, terminal in enumerate(terminals):
        for column_index, phase in enumerate(phases):
            axis: Axes = grid[row_index, column_index]
            selected = (col("terminal") == terminal) & (col("phase") == phase)
            group = observations.filter(selected)
            axis.set_title(f"{names.get(terminal, terminal)} — phase {phase}")
            if group.is_empty():
                axis.text(
                    0.5,
                    0.5,
                    "No validated observations",
                    transform=axis.transAxes,
                    ha="center",
                )
                continue
            group_values = group["value_pu"].to_numpy()
            axis.hist(
                group_values,
                bins=20,
                density=True,
                color="#8db7c2",
                edgecolor="white",
                linewidth=0.7,
            )
            fits = comparison.filter(selected & (col("status") == "fitted"))
            for fit in fits.iter_rows(named=True):
                if fit["model"] != "normal" and not fit["selected"]:
                    continue
                model = MODELS[fit["model"]]
                parameters = (fit["location"], fit["scale"])
                if fit["shape"] is not None:
                    parameters = (fit["shape"], *parameters)
                density = model.pdf(x_values, *parameters)
                density[~isfinite(density)] = float("nan")
                if fit["model"] == "normal":
                    axis.plot(
                        x_values,
                        density,
                        color="#999999",
                        linestyle="--",
                        linewidth=1.8,
                    )
                if fit["selected"]:
                    axis.plot(
                        x_values, density, color="#a74423", linewidth=2.3
                    )
            winner = fits.filter(col("selected"))
            label = (
                str(winner.item(0, "model")).capitalize()
                if winner.height
                else "Fit unavailable"
            )
            axis.text(
                0.97,
                0.94,
                f"{label}\nn = {group.height}\n"
                f"Mean = {group_values.mean():.3f} p.u.\n"
                f"Std = {group_values.std(ddof=0):.3f} p.u.",
                transform=axis.transAxes,
                ha="right",
                va="top",
                fontsize=10,
            )
            axis.grid(axis="y", alpha=0.15)
            axis.set_axisbelow(True)
            axis.spines[["top", "right"]].set_visible(False)
            axis.set_xlim(left, right)
            axis.set_ylim(bottom=0)
            if column_index == 0:
                axis.set_ylabel("Probability density (1/p.u.)")
            if row_index == len(terminals) - 1:
                axis.set_xlabel("Peak voltage (p.u.)")
    scenario = observations.item(0, "scenario")
    sample_size = observations.item(0, "sample_size")
    figure.suptitle(
        f"{scenario} — {sample_size} energizations — phase-to-ground peaks\n"
        "MLE, estimated location; lowest AIC ranks fit, not adequacy",
        fontsize=13,
    )
    figure.legend(
        handles=[
            Patch(facecolor="#8db7c2", label="ATP peak density"),
            Line2D(
                [],
                [],
                color="#a74423",
                linewidth=2.3,
                label="Lowest AIC: normal / gamma / lognormal",
            ),
            Line2D(
                [], [], color="#999999", linestyle="--", label="Fitted normal"
            ),
        ],
        loc="lower center",
        ncol=3,
        frameon=False,
    )
    figure.tight_layout(rect=(0, 0.045, 1, 0.94))
    return figure, tuple(grid.flat)
