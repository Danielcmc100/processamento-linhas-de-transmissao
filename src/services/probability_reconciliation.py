"""Reconcile ATP probability bins with strict direct observations."""

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

from src.parser.statistical_distribution import ATPDistributionBin


@dataclass(frozen=True, slots=True)
class ProbabilityReconciliation:
    """Preserved source and recomputed probability evidence."""

    terminal: str
    phase: str
    interval_number: int
    threshold: float
    unit: str
    source_operator: str
    recomputed_operator: str
    source_count: int
    recomputed_count: int
    boundary_count: int
    source_denominator: int
    recomputed_denominator: int
    source_probability: float
    recomputed_probability: float | None
    source_percentage: float
    recomputed_percentage: float | None
    printed_precision: int
    probability_tolerance: float
    validation_status: str
    reason: str


def reconcile_probability_bin(
    source_bin: ATPDistributionBin,
    direct_values: Iterable[float],
) -> ProbabilityReconciliation:
    """Compare one ATP ``.GE.`` bin with strict direct exceedance.

    ATP printed percentage tolerance is half one unit in its final decimal
    place, converted from percentage points to probability. Values exactly at
    the threshold remain explicit because ATP uses ``>=`` while direct
    evidence uses ``>``.

    Returns:
        Source evidence, direct recomputation, and validation decision.

    Raises:
        ValueError: If a direct value is not finite.
    """
    values = tuple(float(value) for value in direct_values)
    if any(not isfinite(value) for value in values):
        message = "direct values must be finite."
        raise ValueError(message)

    denominator = len(values)
    recomputed_count = sum(value > source_bin.threshold for value in values)
    boundary_count = sum(value == source_bin.threshold for value in values)
    probability = recomputed_count / denominator if denominator else None
    tolerance = 0.5 * 10 ** (-source_bin.printed_precision) / 100.0
    status, reason = _decision(
        source_bin,
        denominator,
        recomputed_count,
        boundary_count,
        probability,
        tolerance,
    )
    return ProbabilityReconciliation(
        terminal=source_bin.terminal,
        phase=source_bin.phase,
        interval_number=source_bin.interval_number,
        threshold=source_bin.threshold,
        unit=source_bin.unit,
        source_operator=source_bin.comparison_operator,
        recomputed_operator=">",
        source_count=source_bin.source_count,
        recomputed_count=recomputed_count,
        boundary_count=boundary_count,
        source_denominator=source_bin.denominator,
        recomputed_denominator=denominator,
        source_probability=source_bin.source_probability,
        recomputed_probability=probability,
        source_percentage=source_bin.source_percentage,
        recomputed_percentage=(
            probability * 100.0 if probability is not None else None
        ),
        printed_precision=source_bin.printed_precision,
        probability_tolerance=tolerance,
        validation_status=status,
        reason=reason,
    )


def _decision(
    source_bin: ATPDistributionBin,
    denominator: int,
    recomputed_count: int,
    boundary_count: int,
    probability: float | None,
    tolerance: float,
) -> tuple[str, str]:
    if denominator != source_bin.denominator:
        return "invalid", "Source and recomputed denominators differ."
    boundary_explains_difference = (
        boundary_count > 0
        and source_bin.source_count == recomputed_count + boundary_count
    )
    if boundary_explains_difference:
        noun = "observation" if boundary_count == 1 else "observations"
        return (
            "qualified",
            f"ATP .GE. includes {boundary_count} boundary {noun} "
            "excluded by strict >.",
        )
    if source_bin.source_count != recomputed_count:
        return "invalid", "Source and recomputed occurrence counts differ."
    if probability is None:
        return "invalid", "Recomputed denominator is zero."
    difference = abs(source_bin.source_probability - probability)
    if difference > tolerance:
        return (
            "invalid",
            "Source and recomputed probabilities exceed printed tolerance.",
        )
    return "valid", "Counts and probabilities agree within tolerance."
