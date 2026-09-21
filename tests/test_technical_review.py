"""Tests for traceable technical-review selection and records."""

from datetime import date
from json import loads

import polars
import pytest

from src.services.technical_review import (
    MethodEvidence,
    PeerObservation,
    ReviewConclusion,
    SupportingEvidence,
    SwitchingCondition,
    TechnicalReviewRecord,
    deserialize_review_records,
    select_review_cases,
    serialize_review_records,
)


def _review_candidates() -> polars.DataFrame:
    return polars.DataFrame({
        "source_file": ["z.lis", "b.lis", "c.lis", "d.lis", "a.lis"],
        "source_sha256": [f"hash-{index}" for index in range(5)],
        "source_lineage": ["line-1", "line-2", "line-3", "line-4", "line-5"],
        "scenario": ["SRPI", "CRPI", "SRPI", "CRPI", "SRPI"],
        "sample_size": [50] * 5,
        "simulation": [5, 2, 3, 4, 1],
        "terminal": ["T_MAN", "T_OPO", "T_MAN", "T_OPO", "T_MAN"],
        "phase": ["A", "B", "C", "A", "B"],
        "source_value": [-320000.0, 250000.0, 410000.0, 230000.0, 120000.0],
        "value_pu": [2.84, 2.22, 3.64, 2.04, 1.07],
        "time": [0.05, 0.02, 0.03, 0.04, 0.01],
        "method_agreement": [4, 2, 1, 1, 0],
        "applicable_method_count": [4, 4, 4, 4, 4],
        "method_disagreement": [False, True, True, True, False],
        "anomaly_candidate": [True, True, True, True, False],
        "score": [1.1, 1.2, 9.0, 1.001, 0.2],
        "threshold": [1.0] * 5,
        "applicability": ["applicable"] * 5,
        "dbscan_score": [0.8, 0.9, 8.0, 0.999, 0.1],
        "dbscan_threshold": [1.0] * 5,
        "dbscan_applicability": ["applicable"] * 5,
    })


def _supporting_evidence(kind: str) -> SupportingEvidence:
    return SupportingEvidence(
        availability="available",
        source=f"{kind}.csv",
        parameters={"model": "same", "output_resolution": 1e-6},
        integration_step=1e-5,
        comparison_tolerance=0.01,
        observed_behavior="Peak converged within tolerance.",
    )


def _record(
    conclusion: ReviewConclusion = ReviewConclusion.UNRESOLVED,
) -> TechnicalReviewRecord:
    return TechnicalReviewRecord(
        review_stratum="agreement",
        source_file="case.lis",
        source_sha256="abc123",
        source_lineage="lineage-1",
        scenario="SRPI",
        sample_size=50,
        base_voltage=112677.0,
        event_definition="absolute_phase_to_ground_maximum",
        simulation=7,
        terminal="T_MAN",
        phase="A",
        source_value=-245000.0,
        value_pu=2.174357,
        time=0.042,
        switching_context=[
            SwitchingCondition(
                switch_number=1,
                opening_time=0.031,
                mean_time=0.03,
                std_dev=0.002,
            )
        ],
        peer_context=[
            PeerObservation(
                terminal="T_MAN",
                phase="B",
                source_value=210000.0,
                value_pu=1.8637,
                time=0.041,
            )
        ],
        method_evidence=[
            MethodEvidence(
                method="kmeans",
                score=1.8,
                threshold=1.2,
                flag=True,
                applicability="applicable",
                reason="Distance exceeds calibrated threshold.",
                group_key="SRPI|lineage-1|T_MAN|A",
                feature_space="value_pu",
                scaling_policy=("standard_scaler_fit_on_calibration_group"),
                configuration_id="kmeans-v1",
            )
        ],
        waveform_evidence=_supporting_evidence("waveform"),
        repeat_simulation_evidence=_supporting_evidence("repeat"),
        reviewer="Engineer One",
        reviewer_qualified=True,
        reviewer_independent=True,
        review_date=date(2026, 9, 21),
        conclusion=conclusion,
        rationale="Source, waveform, and repeat evidence reviewed.",
    )


def test_selection_covers_all_review_strata_deterministically() -> None:
    candidates = _review_candidates()

    first = select_review_cases(candidates.sample(fraction=1.0, seed=9))
    second = select_review_cases(candidates.reverse())

    assert first.select(
        "review_stratum", "source_file", "simulation", "terminal", "phase"
    ).equals(
        second.select(
            "review_stratum",
            "source_file",
            "simulation",
            "terminal",
            "phase",
        )
    )
    assert first["review_stratum"].to_list() == [
        "agreement",
        "disagreement",
        "high_score",
        "boundary",
        "nonflagged_control",
    ]
    assert (
        first.filter(polars.col("review_stratum") == "high_score").item(
            0, "simulation"
        )
        == 3
    )
    assert (
        first.filter(polars.col("review_stratum") == "boundary").item(
            0, "simulation"
        )
        == 4
    )


@pytest.mark.parametrize("source_value", [-245000.0, 245000.0])
def test_record_preserves_complete_identity_and_signed_value(
    source_value: float,
) -> None:
    record = _record().model_copy(update={"source_value": source_value})

    restored = TechnicalReviewRecord.model_validate(record.model_dump())

    assert restored.source_file == "case.lis"
    assert restored.source_sha256 == "abc123"
    assert restored.simulation == 7
    assert restored.source_value == source_value
    assert restored.switching_context[0].opening_time == 0.031
    assert restored.peer_context[0].phase == "B"
    assert restored.method_evidence[0].flag is True


@pytest.mark.parametrize(
    "conclusion",
    [
        ReviewConclusion.DATA_DEFECT,
        ReviewConclusion.SUSPECTED_NUMERICAL_ARTIFACT,
        ReviewConclusion.PHYSICALLY_PLAUSIBLE_EXTREME,
        ReviewConclusion.UNRESOLVED,
    ],
)
def test_exact_conclusion_categories_round_trip(
    conclusion: ReviewConclusion,
) -> None:
    payload = serialize_review_records([_record(conclusion)])
    restored = deserialize_review_records(payload)

    assert restored[0].conclusion is conclusion
    assert loads(payload)[0]["conclusion"] == conclusion.value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("waveform_evidence", SupportingEvidence.unavailable("not saved")),
        (
            "repeat_simulation_evidence",
            SupportingEvidence.unavailable("ATP runtime unavailable"),
        ),
        ("reviewer_qualified", False),
    ],
)
def test_missing_qualified_causal_evidence_forces_unresolved(
    field: str,
    value: object,
) -> None:
    record = _record(ReviewConclusion.SUSPECTED_NUMERICAL_ARTIFACT).model_copy(
        update={field: value}
    )

    validated = TechnicalReviewRecord.model_validate(record.model_dump())

    assert validated.conclusion is ReviewConclusion.UNRESOLVED


def test_unavailable_repeat_simulation_is_explicit_in_serialization() -> None:
    unavailable = SupportingEvidence.unavailable(
        "ATP executable was unavailable."
    )
    record = _record().model_copy(
        update={"repeat_simulation_evidence": unavailable}
    )

    payload = loads(serialize_review_records([record]))

    assert payload[0]["repeat_simulation_evidence"] == {
        "availability": "unavailable",
        "source": None,
        "parameters": {},
        "integration_step": None,
        "comparison_tolerance": None,
        "observed_behavior": None,
        "unavailability_reason": "ATP executable was unavailable.",
    }


def test_available_supporting_evidence_requires_trace_fields() -> None:
    with pytest.raises(ValueError, match="Available evidence requires"):
        SupportingEvidence(
            availability="available",
            source="repeat.csv",
            parameters={},
            integration_step=None,
            comparison_tolerance=None,
            observed_behavior=None,
        )
