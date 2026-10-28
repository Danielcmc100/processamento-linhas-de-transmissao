"""Source-table-first publication figures for thesis-defense evidence."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path

from matplotlib import pyplot
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle
from numpy import (
    arange,
    asarray,
    histogram,
    histogram_bin_edges,
    linspace,
    sort,
)
from polars import DataFrame
from scipy.stats import norm

OKABE_ITO_PALETTE = (
    "#E69F00",
    "#56B4E9",
    "#009E73",
    "#F0E442",
    "#0072B2",
    "#D55E00",
    "#CC79A7",
    "#000000",
)

_MARKERS = ("o", "s", "^", "D", "v", "P", "X", "*")
_LINESTYLES = ("-", "--", "-.", ":")


@dataclass(frozen=True, slots=True)
class FigureContext:
    """Explicit scope shared by every publication figure."""

    scenario: str
    sample_size: int
    terminal: str
    phase: str
    method: str
    unit: str
    threshold: float | None
    status: str

    def __post_init__(self) -> None:
        """Reject incomplete or invalid visible figure context."""
        text_fields = (
            self.scenario,
            self.terminal,
            self.phase,
            self.method,
            self.unit,
            self.status,
        )
        if any(not value.strip() for value in text_fields):
            raise ValueError("Figure context fields must not be empty.")
        if type(self.sample_size) is not int or self.sample_size < 1:
            raise ValueError("sample_size must be a positive integer.")
        if self.threshold is not None and not isfinite(self.threshold):
            raise ValueError("threshold must be finite when provided.")


@dataclass(frozen=True, slots=True)
class ExportedFigure:
    """Paths and raster resolution for one publication export."""

    svg_path: Path
    png_path: Path
    dpi: int


def plot_distribution_qq(
    source: DataFrame,
    context: FigureContext,
    *,
    comparison_source: DataFrame | None = None,
) -> tuple[Figure, tuple[Axes, Axes]]:
    """Plot histogram, fitted Gaussian density, and normal Q-Q evidence.

    Returns:
        Figure and histogram/Q-Q axes built from one saved source table.

    Raises:
        ValueError: If required source fields or usable values are absent.
    """
    _require_columns(
        source,
        (
            "value_pu",
            "fitted_mean",
            "fitted_standard_deviation",
            "adequacy_status",
        ),
    )
    values = asarray(source["value_pu"].drop_nulls().to_list(), dtype=float)
    if len(values) < 2 or not all(isfinite(float(value)) for value in values):
        raise ValueError("value_pu requires at least two finite values.")
    fitted_mean = _constant_float(source, "fitted_mean")
    fitted_std = _constant_float(source, "fitted_standard_deviation")
    if fitted_std <= 0.0:
        raise ValueError(
            "fitted_standard_deviation must be greater than zero."
        )
    adequacy = _constant_text(source, "adequacy_status")
    adequacy = {
        "rejected": "rejeitada",
        "not_rejected": "não rejeitada",
        "undersized": "amostra insuficiente",
        "degenerate": "distribuição degenerada",
    }.get(adequacy, adequacy)
    comparison = source if comparison_source is None else comparison_source
    all_values = comparison["value_pu"].to_numpy()
    bins = histogram_bin_edges(all_values, bins="auto")
    lower, upper = float(bins[0]), float(bins[-1])
    margin = (upper - lower) * 0.04
    density_max = 0.0
    for group in comparison.partition_by(
        "fitted_mean", "fitted_standard_deviation", "adequacy_status"
    ):
        density, _ = histogram(
            group["value_pu"].to_numpy(), bins=bins, density=True
        )
        standard_deviation = float(group["fitted_standard_deviation"][0])
        peak = float(norm.pdf(0.0, scale=standard_deviation))
        density_max = max(density_max, float(density.max()), peak)

    figure, raw_axes = pyplot.subplots(1, 2, figsize=(7.2, 3.5))
    histogram_axis, qq_axis = raw_axes
    histogram_axis.hist(
        values,
        bins=bins,
        density=True,
        color=OKABE_ITO_PALETTE[1],
        edgecolor="#000000",
        alpha=0.55,
        label="Empírica",
    )
    density_x = linspace(float(values.min()), float(values.max()), 240)
    histogram_axis.plot(
        density_x,
        norm.pdf(density_x, loc=fitted_mean, scale=fitted_std),
        color=OKABE_ITO_PALETTE[5],
        linestyle="--",
        linewidth=2.0,
        label="Ajuste gaussiano",
    )
    _draw_context_threshold(histogram_axis, context)
    histogram_axis.set_xlabel(f"Sobretensão ({context.unit})")
    histogram_axis.set_ylabel("Densidade")
    histogram_axis.set_title("Distribuição e ajuste gaussiano", fontsize=10)
    if (
        context.threshold is not None
        and not lower <= context.threshold <= upper
    ):
        histogram_axis.lines[-1].set_label("_nolegend_")
    histogram_axis.legend(
        fontsize=9,
        loc=(
            "upper left"
            if fitted_mean > (lower + upper) / 2
            else "upper right"
        ),
    )

    probabilities = (arange(len(values), dtype=float) + 0.5) / len(values)
    theoretical = norm.ppf(probabilities)
    observed = sort(values)
    qq_axis.scatter(
        theoretical,
        observed,
        color=OKABE_ITO_PALETTE[4],
        marker="o",
        label="Quantis observados",
    )
    qq_axis.plot(
        theoretical,
        fitted_mean + fitted_std * theoretical,
        color=OKABE_ITO_PALETTE[5],
        linestyle="--",
        label="Referência gaussiana",
    )
    qq_axis.set_xlabel("Quantis teóricos normais")
    qq_axis.set_ylabel(f"Quantis observados ({context.unit})")
    qq_axis.set_title(f"Gráfico Q-Q | Adequação: {adequacy}", fontsize=10)
    qq_axis.legend(fontsize=9)
    histogram_axis.set_xlim(lower - margin, upper + margin)
    histogram_axis.set_ylim(0.0, density_max * 1.12)
    qq_axis.set_ylim(lower - margin, upper + margin)
    # Reference quantiles and fitted lines share the same comparison window.
    max_count = max(
        group.height
        for group in comparison.partition_by(
            "fitted_mean", "fitted_standard_deviation", "adequacy_status"
        )
    )
    quantile_limit = float(norm.ppf(1.0 - 0.5 / max_count)) * 1.05
    qq_axis.set_xlim(-quantile_limit, quantile_limit)
    threshold_note = ""
    if context.threshold is not None:
        exceedances = int((values > context.threshold).sum())
        threshold = f"{context.threshold:g}".replace(".", ",")
        outside = not lower - margin <= context.threshold <= upper + margin
        location = "; fora da janela" if outside else ""
        denominator = f"{len(values):,}".replace(",", ".")
        threshold_note = (
            f"Limiar {threshold} {context.unit}{location}: "
            f"{exceedances}/{denominator} excedências (>)."
        )
    figure.suptitle(
        f"{context.scenario} | {context.terminal}, fase {context.phase} | "
        + f"N = {len(values):,}".replace(",", "."),
        fontsize=12,
    )
    figure.text(0.5, 0.015, threshold_note, ha="center", fontsize=11)
    for axis in (histogram_axis, qq_axis):
        axis.grid(visible=True, linestyle=":", alpha=0.35)
    figure.tight_layout(rect=(0.0, 0.065, 1.0, 0.94))
    return figure, (histogram_axis, qq_axis)


def plot_probability_comparison(
    source: DataFrame,
    context: FigureContext,
) -> tuple[Figure, Axes]:
    """Plot empirical and Gaussian exceedance with empirical uncertainty.

    Returns:
        Figure and probability axis.
    """
    _require_columns(
        source,
        (
            "threshold",
            "empirical_probability",
            "gaussian_probability",
            "confidence_interval_lower",
            "confidence_interval_upper",
            "adequacy_status",
            "denominator",
        ),
    )
    thresholds = source["threshold"].to_list()
    empirical = source["empirical_probability"].to_list()
    gaussian = source["gaussian_probability"].to_list()
    lower = source["confidence_interval_lower"].to_list()
    upper = source["confidence_interval_upper"].to_list()
    adequacy = _constant_text(source, "adequacy_status")
    denominator = _constant_int(source, "denominator")

    figure, axis = pyplot.subplots(figsize=(7.5, 4.8))
    axis.plot(
        thresholds,
        empirical,
        color=OKABE_ITO_PALETTE[4],
        marker="o",
        linestyle="-",
        label="Empírica",
    )
    axis.plot(
        thresholds,
        gaussian,
        color=OKABE_ITO_PALETTE[5],
        marker="s",
        linestyle="--",
        label="Gaussiana",
    )
    axis.fill_between(
        thresholds,
        # matplotlib-stubs incorrectly restricts array bounds to scalars.
        asarray(lower, dtype=float),  # pyright: ignore[reportArgumentType]
        asarray(upper, dtype=float),  # pyright: ignore[reportArgumentType]
        color=OKABE_ITO_PALETTE[1],
        alpha=0.25,
        label="IC empírico de 95%",
    )
    _draw_context_threshold(axis, context)
    axis.set_xlabel(f"Limiar de sobretensão ({context.unit})")
    axis.set_ylabel("Probabilidade de excedência")
    axis.set_ylim(0.0, 1.0)
    axis.set_title(
        f"Excedência empírica versus gaussiana | n = {denominator}\n"
        f"Adequação: {adequacy}"
    )
    axis.legend(fontsize=8)
    _finish(figure, (axis,), context)
    return figure, axis


def plot_convergence(
    source: DataFrame,
    context: FigureContext,
    *,
    comparison_source: DataFrame | None = None,
) -> tuple[Figure, tuple[Axes, Axes, Axes]]:
    """Compare saved descriptive, candidate and probability evidence by N.

    Returns:
        Figure and three axes with corresponding cross-scenario scales.

    Raises:
        ValueError: If required columns or present sample sizes are absent.
    """
    required = (
        "sample_size",
        "mean",
        "percentile_95",
        "candidate_rate",
        "empirical_probability",
        "confidence_interval_lower",
        "confidence_interval_upper",
        "coverage_status",
        "independence_limitation",
    )
    _require_columns(source, required)
    comparison = source if comparison_source is None else comparison_source
    _require_columns(comparison, required)
    present = source.filter(source["coverage_status"] == "present").sort(
        "sample_size"
    )
    pooled = comparison.filter(comparison["coverage_status"] == "present")
    if present.is_empty() or pooled.is_empty():
        raise ValueError("Convergence source has no present sample sizes.")
    figure, raw_axes = pyplot.subplots(3, 1, figsize=(9.5, 8.0), sharex=True)
    descriptive, candidates, probability = raw_axes
    sizes = present["sample_size"].to_list()
    for column, label, color, marker, style in (
        ("mean", "Média", OKABE_ITO_PALETTE[4], "o", "-"),
        ("percentile_95", "Percentil 95", OKABE_ITO_PALETTE[5], "s", "--"),
    ):
        descriptive.plot(
            sizes,
            present[column].to_list(),
            label=label,
            color=color,
            marker=marker,
            linestyle=style,
        )
    descriptive.set_ylabel(f"Tensão ({context.unit})", fontsize=12)
    descriptive.set_title("Medidas descritivas", fontsize=13)
    candidates.plot(
        sizes,
        present["candidate_rate"].to_list(),
        color=OKABE_ITO_PALETTE[5],
        marker="s",
        label="União dos critérios",
    )
    for size, rate in zip(sizes, present["candidate_rate"], strict=True):
        candidates.annotate(
            f"{float(rate):.2%}".replace(".", ","),
            (size, rate),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )
    candidates.set_ylabel("Taxa de candidatos", fontsize=12)
    candidates.set_title("Candidatos analíticos", fontsize=13)
    empirical = asarray(present["empirical_probability"], dtype=float)
    lower = asarray(present["confidence_interval_lower"], dtype=float)
    upper = asarray(present["confidence_interval_upper"], dtype=float)
    probability.errorbar(
        sizes,
        empirical,
        yerr=asarray([empirical - lower, upper - empirical]),
        color=OKABE_ITO_PALETTE[4],
        marker="o",
        capsize=5,
        label="Empírica e IC de Wilson de 95%",
    )
    threshold = (
        f"{context.threshold:g}".replace(".", ",")
        if context.threshold is not None
        else "declarado"
    )
    probability.set_title(
        f"Excedência do limiar {threshold} {context.unit}", fontsize=13
    )
    probability.set_ylabel("Probabilidade", fontsize=12)
    voltage_values = [
        float(value)
        for column in ("mean", "percentile_95")
        for value in pooled[column].drop_nulls()
    ]
    voltage_min, voltage_max = min(voltage_values), max(voltage_values)
    margin = max((voltage_max - voltage_min) * 0.12, 0.01)
    descriptive.set_ylim(voltage_min - margin, voltage_max + margin)
    candidate_max = max(float(value) for value in pooled["candidate_rate"])
    candidates.set_ylim(0.0, max(candidate_max * 1.15, 0.01))
    probability_max = max(
        float(value) for value in pooled["confidence_interval_upper"]
    )
    probability.set_ylim(
        -max(probability_max * 0.06, 0.0001),
        max(probability_max * 1.15, 0.001),
    )
    for axis in raw_axes:
        axis.set_xscale("log")
        axis.set_xticks(sizes)
        axis.set_xticklabels([f"{size:,}".replace(",", ".") for size in sizes])
        axis.tick_params(labelsize=11)
        axis.grid(visible=True, linestyle=":", alpha=0.35)
        axis.legend(fontsize=11, loc="upper right")
    legend_location = (
        "lower right"
        if min(float(value) for value in present["mean"])
        > (voltage_min + voltage_max) / 2
        else "upper right"
    )
    descriptive.legend(fontsize=11, loc=legend_location)
    probability.set_xlabel("Número de simulações (N)", fontsize=12)
    scope = f"{min(sizes):,}–{max(sizes):,}".replace(",", ".")
    figure.suptitle(
        f"{context.scenario} | {context.terminal}, fase {context.phase} | "
        f"N = {scope}",
        fontsize=13,
    )
    figure.text(
        0.5,
        0.015,
        "Comparação descritiva; independência e aninhamento "
        "não estabelecidos.",
        ha="center",
        fontsize=11,
    )
    figure.tight_layout(rect=(0.0, 0.045, 1.0, 0.96))
    return figure, (descriptive, candidates, probability)


def plot_cluster_anomalies(
    source: DataFrame,
    context: FigureContext,
) -> tuple[Figure, Axes]:
    """Separate descriptive cluster colors from anomaly-evidence markers.

    Returns:
        Figure and cluster-evidence axis.
    """
    _require_columns(
        source,
        (
            "simulation",
            "value_pu",
            "cluster",
            "anomaly_flag",
            "score",
            "threshold",
        ),
    )
    figure, axis = pyplot.subplots(figsize=(8.0, 4.8))
    clusters = sorted(source["cluster"].drop_nulls().unique().to_list())
    for index, cluster in enumerate(clusters):
        rows = source.filter(source["cluster"] == cluster)
        axis.scatter(
            rows["simulation"],
            rows["value_pu"],
            color=OKABE_ITO_PALETTE[index % len(OKABE_ITO_PALETTE)],
            marker=MarkerStyle(_MARKERS[index % len(_MARKERS)]),
            alpha=0.75,
            label=f"Cluster {cluster}",
        )
    candidates = source.filter(source["anomaly_flag"])
    if not candidates.is_empty():
        axis.scatter(
            candidates["simulation"],
            candidates["value_pu"],
            facecolors="none",
            edgecolors="#000000",
            marker=MarkerStyle("D"),
            s=90,
            linewidths=1.5,
            label="Candidato analítico",
        )
    _draw_context_threshold(axis, context)
    score_threshold = _constant_float(source, "threshold")
    axis.set_xlabel("Simulação")
    axis.set_ylabel(f"Sobretensão ({context.unit})")
    axis.set_title(
        "Agrupamento e evidência | cor = cluster descritivo; "
        "marcador = evidência de anomalia\n"
        f"Limiar do escore: {score_threshold:g}"
    )
    axis.legend(fontsize=8)
    _finish(figure, (axis,), context)
    return figure, axis


def plot_method_agreement(
    source: DataFrame,
    context: FigureContext,
) -> tuple[Figure, Axes]:
    """Plot agreement, disagreement, N/A, and candidate counts.

    Returns:
        Figure and grouped-count axis.
    """
    _require_columns(source, ("status", "count", "candidate_count"))
    statuses = ("agreement", "disagreement", "non_applicable")
    labels = ("Concordância", "Discordância", "Não aplicável")
    count_by_status = {
        str(row["status"]): int(row["count"])
        for row in source.iter_rows(named=True)
    }
    candidates_by_status = {
        str(row["status"]): int(row["candidate_count"])
        for row in source.iter_rows(named=True)
    }
    positions = arange(len(statuses), dtype=float)
    figure, axis = pyplot.subplots(figsize=(7.5, 4.8))
    axis.bar(
        positions - 0.18,
        [count_by_status.get(status, 0) for status in statuses],
        width=0.36,
        color=OKABE_ITO_PALETTE[1],
        edgecolor="#000000",
        hatch="//",
        label="Observações",
    )
    axis.bar(
        positions + 0.18,
        [candidates_by_status.get(status, 0) for status in statuses],
        width=0.36,
        color=OKABE_ITO_PALETTE[5],
        edgecolor="#000000",
        hatch="xx",
        label="Candidatos",
    )
    axis.set_xticks(positions, labels)
    axis.set_xlabel("Estado da comparação")
    axis.set_ylabel("Contagem")
    axis.set_title("Concordância entre métodos, discordância e aplicabilidade")
    axis.legend(fontsize=8)
    _finish(figure, (axis,), context)
    return figure, axis


def plot_benchmark(
    source: DataFrame,
    context: FigureContext,
) -> tuple[Figure, Axes]:
    """Plot controlled benchmark recall and explicit N/A conditions.

    Returns:
        Figure and intervention-intensity axis.
    """
    _require_columns(
        source,
        (
            "intervention_family",
            "intervention_intensity",
            "method",
            "recall",
            "benchmark_applicability",
        ),
    )
    figure, axis = pyplot.subplots(figsize=(8.0, 4.8))
    applicable = source.filter(
        source["benchmark_applicability"] == "applicable"
    )
    group_columns = ("method", "intervention_family")
    for index, group in enumerate(
        applicable.partition_by(group_columns, maintain_order=True)
    ):
        ordered = group.sort("intervention_intensity")
        method = str(ordered.item(0, "method"))
        family = str(ordered.item(0, "intervention_family"))
        axis.plot(
            ordered["intervention_intensity"],
            ordered["recall"],
            color=OKABE_ITO_PALETTE[index % len(OKABE_ITO_PALETTE)],
            marker=_MARKERS[index % len(_MARKERS)],
            linestyle=_LINESTYLES[index % len(_LINESTYLES)],
            label=f"{method} | {family}",
        )
    non_applicable = source.filter(
        source["benchmark_applicability"] == "non_applicable"
    )
    if not non_applicable.is_empty():
        axis.scatter(
            non_applicable["intervention_intensity"],
            [0.0] * non_applicable.height,
            color="#000000",
            marker=MarkerStyle("x"),
            s=70,
            label="Não aplicável",
        )
    axis.set_xlabel("Intensidade da intervenção")
    axis.set_ylabel("Revocação")
    axis.set_ylim(-0.03, 1.03)
    axis.set_title("Intervenção controlada por família, intensidade e método")
    axis.legend(fontsize=8)
    _finish(figure, (axis,), context)
    return figure, axis


def plot_sensitivity(
    source: DataFrame,
    context: FigureContext,
) -> tuple[Figure, Axes]:
    """Plot identity Jaccard across one frozen varied parameter.

    Returns:
        Figure and candidate-stability axis.
    """
    _require_columns(
        source,
        (
            "varied_parameter",
            "varied_value",
            "fixed_controls",
            "identity_jaccard",
            "stability_threshold",
            "qualification",
            "applicability",
        ),
    )
    parameter = _constant_text(source, "varied_parameter")
    controls = _constant_text(source, "fixed_controls")
    threshold = _constant_float(source, "stability_threshold")
    qualification = _qualification_label(
        _constant_text(source, "qualification")
    )
    applicable = source.filter(source["applicability"] == "applicable")
    if applicable.is_empty():
        raise ValueError("Sensitivity source has no applicable result.")
    positions = arange(applicable.height, dtype=float)
    figure, axis = pyplot.subplots(figsize=(8.0, 4.8))
    axis.plot(
        positions,
        applicable["identity_jaccard"],
        color=OKABE_ITO_PALETTE[4],
        marker="o",
        linestyle="-",
        label="Sobreposição de identidades",
    )
    axis.axhline(
        threshold,
        color=OKABE_ITO_PALETTE[5],
        linestyle="--",
        label=f"Limiar de estabilidade: {threshold:.2f}",
    )
    axis.set_xticks(
        positions,
        [str(value) for value in applicable["varied_value"].to_list()],
    )
    axis.set_ylim(0.0, 1.02)
    axis.set_xlabel(f"Parâmetro variado: {parameter}")
    axis.set_ylabel("Jaccard das identidades candidatas")
    axis.set_title(
        f"Sensibilidade: {qualification} | Controles fixos: {controls}"
    )
    axis.legend(fontsize=8)
    _finish(figure, (axis,), context)
    return figure, axis


def export_publication_figure(
    figure: Figure,
    output_stem: Path,
    *,
    dpi: int = 300,
) -> ExportedFigure:
    """Export one figure as SVG and a raster fallback of at least 300 DPI.

    Returns:
        Written SVG/PNG paths and raster resolution.

    Raises:
        ValueError: If output stem has a suffix or raster DPI is too low.
    """
    if output_stem.suffix:
        raise ValueError("output_stem must not include a file extension.")
    if type(dpi) is not int or dpi < 300:
        raise ValueError("dpi must be an integer of at least 300.")
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    svg_path = output_stem.with_suffix(".svg")
    png_path = output_stem.with_suffix(".png")
    figure.savefig(svg_path, format="svg", bbox_inches="tight")
    figure.savefig(png_path, format="png", dpi=dpi, bbox_inches="tight")
    return ExportedFigure(svg_path=svg_path, png_path=png_path, dpi=dpi)


def _scope(context: FigureContext) -> str:
    """Build Portuguese scope text displayed on every figure."""
    threshold = (
        "sem limiar"
        if context.threshold is None
        else f"limiar: {context.threshold:g} {context.unit}"
    )
    return (
        f"{context.scenario} | n={context.sample_size} | {context.terminal} | "
        f"fase {context.phase} | método: {context.method} | {threshold} | "
        f"estado: {context.status}"
    )


def _finish(
    figure: Figure,
    axes: tuple[Axes, ...],
    context: FigureContext,
) -> None:
    """Apply shared accessible publication styling and visible scope."""
    figure.suptitle(_scope(context), fontsize=10)
    for axis in axes:
        axis.grid(visible=True, linestyle=":", alpha=0.35)
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))


def _draw_context_threshold(axis: Axes, context: FigureContext) -> None:
    """Draw declared physical threshold when present."""
    if context.threshold is None:
        return
    axis.axvline(
        context.threshold,
        color="#000000",
        linestyle=":",
        linewidth=1.2,
        label=f"Limiar: {context.threshold:g} {context.unit}",
    )


def _require_columns(source: DataFrame, required: tuple[str, ...]) -> None:
    """Fail closed when a figure source lacks declared fields."""
    missing = [column for column in required if column not in source.columns]
    if missing:
        raise ValueError(
            f"Missing required source columns: {', '.join(missing)}."
        )
    if source.is_empty():
        raise ValueError("Figure source table must not be empty.")


def _constant_text(source: DataFrame, column: str) -> str:
    """Read one non-null constant text field from a source table."""
    values = source[column].drop_nulls().unique().to_list()
    if len(values) != 1 or not str(values[0]).strip():
        raise ValueError(f"{column} must contain one non-empty value.")
    return str(values[0])


def _constant_float(source: DataFrame, column: str) -> float:
    """Read one finite constant numeric field from a source table."""
    values = source[column].drop_nulls().unique().to_list()
    if len(values) != 1:
        raise ValueError(f"{column} must contain one value.")
    value = float(values[0])
    if not isfinite(value):
        raise ValueError(f"{column} must be finite.")
    return value


def _constant_int(source: DataFrame, column: str) -> int:
    """Read one constant integer field from a source table."""
    values = source[column].drop_nulls().unique().to_list()
    if len(values) != 1 or type(values[0]) is not int:
        raise ValueError(f"{column} must contain one integer value.")
    return int(values[0])


def _qualification_label(qualification: str) -> str:
    """Translate frozen sensitivity qualification for manuscript figures."""
    labels = {
        "stable": "Estável",
        "sensitive": "Sensível",
        "non_applicable": "Não aplicável",
    }
    return labels.get(qualification, qualification)
