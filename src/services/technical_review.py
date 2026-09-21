"""Traceable selection and records for technical anomaly review.

Analytical candidates do not establish physical or numerical causes. Causal
conclusions require waveform evidence, repeat-simulation evidence, and a
qualified reviewer; otherwise records remain unresolved.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from json import dumps, loads
from math import isfinite
from typing import Literal, Self

from polars import DataFrame, Int64, String
from pydantic import BaseModel, ConfigDict, Field, model_validator

_STRATA = (
    "agreement",
    "disagreement",
    "high_score",
    "boundary",
    "nonflagged_control",
)
_SELECTION_COLUMNS = (
    "source_file",
    "simulation",
    "terminal",
    "phase",
    "scenario",
    "source_lineage",
    "method_agreement",
    "method_disagreement",
    "anomaly_candidate",
)
_SCORE_COLUMNS = (
    ("score", "threshold", "applicability"),
    (
        "modified_mad_score",
        "mad_threshold",
        "mad_applicability",
    ),
    (
        "dbscan_score",
        "dbscan_threshold",
        "dbscan_applicability",
    ),
)

JsonScalar = str | int | float | bool | None


class ReviewConclusion(str, Enum):
    """Permitted case-specific technical-review conclusions."""

    DATA_DEFECT = "data defect"
    SUSPECTED_NUMERICAL_ARTIFACT = "suspected numerical artifact"
    PHYSICALLY_PLAUSIBLE_EXTREME = "physically plausible extreme"
    UNRESOLVED = "unresolved"


class SwitchingCondition(BaseModel):
    """One switching event associated with a reviewed simulation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    switch_number: int
    opening_time: float
    mean_time: float | None = None
    std_dev: float | None = None


class PeerObservation(BaseModel):
    """Another phase or terminal from the reviewed simulation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    terminal: str
    phase: str
    source_value: float
    value_pu: float
    time: float


class MethodEvidence(BaseModel):
    """Explicit Boolean evidence emitted by one analytical method."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    method: str
    score: float | None
    threshold: float | None
    flag: bool | None
    applicability: Literal["applicable", "non_applicable"]
    reason: str | None
    group_key: str
    feature_space: str
    scaling_policy: str
    configuration_id: str


class SupportingEvidence(BaseModel):
    """Waveform or repeat-simulation evidence with explicit availability."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    availability: Literal["available", "unavailable"]
    source: str | None = None
    parameters: dict[str, JsonScalar] = Field(default_factory=dict)
    integration_step: float | None = None
    comparison_tolerance: float | None = None
    observed_behavior: str | None = None
    unavailability_reason: str | None = None

    @classmethod
    def unavailable(cls, reason: str) -> Self:
        """Build explicit unavailable evidence with its reason."""
        return cls(
            availability="unavailable",
            unavailability_reason=reason,
        )

    @model_validator(mode="after")
    def validate_trace_fields(self) -> Self:
        """Require complete trace fields for available evidence."""
        if self.availability == "available":
            required = (
                self.source,
                self.parameters,
                self.integration_step,
                self.comparison_tolerance,
                self.observed_behavior,
            )
            missing = any(
                value is None or value == {} or value == ""
                for value in required
            )
            if missing:
                message = (
                    "Available evidence requires source, parameters, "
                    "integration step, comparison tolerance, and observed "
                    "behavior."
                )
                raise ValueError(message)
            if self.unavailability_reason is not None:
                message = (
                    "Available evidence cannot have an unavailability reason."
                )
                raise ValueError(message)
        elif not self.unavailability_reason:
            message = "Unavailable evidence requires a reason."
            raise ValueError(message)
        return self


class TechnicalReviewRecord(BaseModel):
    """One signed, source-traceable technical-review record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    review_stratum: Literal[
        "agreement",
        "disagreement",
        "high_score",
        "boundary",
        "nonflagged_control",
    ]
    source_file: str
    source_sha256: str
    source_lineage: str
    scenario: str
    sample_size: int
    base_voltage: float
    event_definition: str
    simulation: int
    terminal: str
    phase: str
    source_value: float
    value_pu: float
    time: float
    switching_context: list[SwitchingCondition]
    peer_context: list[PeerObservation]
    method_evidence: list[MethodEvidence]
    waveform_evidence: SupportingEvidence
    repeat_simulation_evidence: SupportingEvidence
    reviewer: str
    reviewer_qualified: bool
    reviewer_independent: bool
    review_date: date
    conclusion: ReviewConclusion
    rationale: str

    @model_validator(mode="after")
    def enforce_causal_evidence(self) -> Self:
        """Force unresolved status when qualified causal evidence is absent."""
        evidence_is_complete = (
            self.waveform_evidence.availability == "available"
            and self.repeat_simulation_evidence.availability == "available"
            and self.reviewer_qualified
        )
        if not evidence_is_complete:
            object.__setattr__(
                self,
                "conclusion",
                ReviewConclusion.UNRESOLVED,
            )
        return self


def select_review_cases(
    evidence: DataFrame,
    *,
    cases_per_stratum: int = 1,
) -> DataFrame:
    """Select deterministic representative rows for five review strata.

    High-score and boundary rankings use explicit applicable score-threshold
    pairs. Selection preserves input columns and adds stratum and within-
    stratum rank. A source row may represent multiple strata because those
    properties overlap by definition.

    Returns:
        Selected evidence rows ordered by declared stratum and rank.

    Raises:
        ValueError: If selection inputs or count are invalid.
    """
    if cases_per_stratum < 1:
        raise ValueError("cases_per_stratum must be at least one.")
    _validate_selection_columns(evidence)
    output_schema = {
        **evidence.schema,
        "review_stratum": String,
        "selection_rank": Int64,
    }
    if evidence.is_empty():
        return DataFrame(schema=output_schema)

    rows = list(evidence.iter_rows(named=True))
    selected: list[dict[str, object]] = []
    for stratum in _STRATA:
        eligible = _eligible_rows(rows, stratum)
        ranked = sorted(
            eligible,
            key=lambda row: _ranking_key(row, stratum),
        )
        for rank, row in enumerate(ranked[:cases_per_stratum], start=1):
            selected.append({
                **row,
                "review_stratum": stratum,
                "selection_rank": rank,
            })

    return DataFrame(selected, schema=output_schema, strict=False)


def serialize_review_records(
    records: list[TechnicalReviewRecord],
) -> str:
    """Serialize validated review records into deterministic JSON."""
    payload = [
        TechnicalReviewRecord.model_validate(record.model_dump()).model_dump(
            mode="json"
        )
        for record in records
    ]
    return dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def deserialize_review_records(payload: str) -> list[TechnicalReviewRecord]:
    """Deserialize and validate technical-review JSON records.

    Returns:
        Validated records with unresolved fallback enforced.

    Raises:
        ValueError: If top-level JSON is not a list.
    """
    decoded: object = loads(payload)
    if not isinstance(decoded, list):
        raise ValueError("Technical review payload must be a JSON list.")
    return [TechnicalReviewRecord.model_validate(item) for item in decoded]


def _validate_selection_columns(evidence: DataFrame) -> None:
    """Validate columns needed for deterministic strata selection."""
    missing = [
        column for column in _SELECTION_COLUMNS if column not in evidence
    ]
    if missing:
        raise ValueError(
            "Required review selection columns are missing: "
            + ", ".join(missing)
            + "."
        )
    available_pairs = [
        pair
        for pair in _SCORE_COLUMNS
        if all(column in evidence for column in pair)
    ]
    if not available_pairs:
        raise ValueError(
            "At least one explicit score, threshold, and applicability "
            "column set is required."
        )


def _eligible_rows(
    rows: list[dict[str, object]],
    stratum: str,
) -> list[dict[str, object]]:
    """Return rows eligible for one declared review stratum."""
    if stratum == "agreement":
        return [
            row
            for row in rows
            if _integer(row.get("method_agreement")) >= 2
            and not bool(row.get("method_disagreement"))
        ]
    if stratum == "disagreement":
        return [row for row in rows if bool(row.get("method_disagreement"))]
    if stratum in {"high_score", "boundary"}:
        return [
            row
            for row in rows
            if bool(row.get("anomaly_candidate")) and _score_metrics(row)
        ]
    return [row for row in rows if not bool(row.get("anomaly_candidate"))]


def _ranking_key(
    row: dict[str, object],
    stratum: str,
) -> tuple[object, ...]:
    """Build stable evidence-first selection ordering."""
    identity = _identity_key(row)
    if stratum == "agreement":
        return (-_integer(row.get("method_agreement")), *identity)
    if stratum == "high_score":
        return (-max(_score_metrics(row)), *identity)
    if stratum == "boundary":
        return (min(_boundary_metrics(row)), *identity)
    return identity


def _score_metrics(row: dict[str, object]) -> list[float]:
    """Return absolute score-to-threshold ratios for applicable methods."""
    ratios: list[float] = []
    for score_column, threshold_column, applicability_column in _SCORE_COLUMNS:
        if row.get(applicability_column) != "applicable":
            continue
        score = _finite_float(row.get(score_column))
        threshold = _finite_float(row.get(threshold_column))
        if score is None or threshold is None:
            continue
        denominator = abs(threshold)
        ratios.append(abs(score) / denominator if denominator else abs(score))
    return ratios


def _boundary_metrics(row: dict[str, object]) -> list[float]:
    """Return normalized distances from applicable score thresholds."""
    distances: list[float] = []
    for score_column, threshold_column, applicability_column in _SCORE_COLUMNS:
        if row.get(applicability_column) != "applicable":
            continue
        score = _finite_float(row.get(score_column))
        threshold = _finite_float(row.get(threshold_column))
        if score is None or threshold is None:
            continue
        denominator = abs(threshold)
        difference = abs(abs(score) - denominator)
        normalized = difference / denominator if denominator else difference
        distances.append(normalized)
    return distances


def _identity_key(row: dict[str, object]) -> tuple[object, ...]:
    """Return stable source and observation ordering key."""
    return (
        str(row.get("scenario", "")),
        str(row.get("source_lineage", "")),
        str(row.get("terminal", "")),
        str(row.get("phase", "")),
        str(row.get("source_file", "")),
        _integer(row.get("simulation")),
    )


def _integer(value: object) -> int:
    """Return integer selection value with deterministic null fallback."""
    return int(value) if isinstance(value, int) else 0


def _finite_float(value: object) -> float | None:
    """Return finite float or null for invalid score metadata."""
    if not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if isfinite(converted) else None
