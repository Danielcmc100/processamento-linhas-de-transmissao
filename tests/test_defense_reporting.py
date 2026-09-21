"""Tests for traceable thesis-defense source and LaTeX tables."""

from json import loads
from pathlib import Path

import polars
import pytest

from src.services.defense_reporting import (
    DefenseReportingResult,
    RoundingPolicy,
    generate_defense_tables,
)


def _probability() -> polars.DataFrame:
    return polars.DataFrame({
        "scenario": ["SRPI"],
        "sample_size": [50],
        "terminal": ["T_OPO"],
        "phase": ["A"],
        "event_definition": ["value_pu > 2 p.u."],
        "threshold": [2.0],
        "occurrence_count": [7],
        "denominator": [50],
        "empirical_probability": [0.123456789012345],
        "confidence_interval_lower": [0.051234567890123],
        "confidence_interval_upper": [0.234567890123456],
        "validation_status": ["qualified"],
    })


def _benchmark() -> polars.DataFrame:
    return polars.DataFrame({
        "intervention_family": ["point_10%"],
        "intervention_intensity": [1.5],
        "method": ["kmeans_distance"],
        "true_positive": [4],
        "false_positive": [1],
        "true_negative": [10],
        "false_negative": [2],
        "precision": [0.8],
        "recall": [2 / 3],
        "f1": [0.7272727272727273],
        "false_positive_rate": [1 / 11],
        "precision_reason": [None],
        "recall_reason": [None],
        "f1_reason": [None],
        "false_positive_rate_reason": [None],
    })


def _convergence() -> polars.DataFrame:
    return polars.DataFrame({
        "scenario": ["SRPI"],
        "sample_size": [10_000],
        "terminal": ["T_OPO"],
        "phase": ["A"],
        "mean": [1.87654321],
        "percentile_95": [2.12345678],
        "empirical_probability": [0.01234567],
        "confidence_interval_width": [0.00456789],
        "fitted_model_status": ["not_rejected"],
        "candidate_count": [23],
        "candidate_rate": [0.0023],
        "grouping_policy": ["scenario|lineage|terminal|phase"],
        "method_policy": ["frozen_v1"],
        "comparison_status": ["comparable"],
    })


def _review() -> polars.DataFrame:
    return polars.DataFrame({
        "source_file": ["caso_1.lis"],
        "source_sha256": ["abc123"],
        "simulation": [7],
        "terminal": ["T_MAN"],
        "phase": ["B"],
        "source_value": [-245000.123456],
        "value_pu": [2.17435791],
        "method_evidence": ["kmeans_distance;dbscan_noise"],
        "conclusion": ["unresolved"],
        "reviewer": ["Revisor & equipe_1"],
        "review_date": ["2026-09-21"],
        "rationale": ["Sem forma de onda: 50% pendente."],
    })


def _generate(output_dir: Path) -> DefenseReportingResult:
    return generate_defense_tables(
        output_dir,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=_review(),
        rounding=RoundingPolicy(decimal_places=4),
        generator_version="1.2.3",
    )


def test_machine_csv_preserves_precision_while_latex_rounds(
    tmp_path: Path,
) -> None:
    _generate(tmp_path)

    source = (tmp_path / "probability.csv").read_text(encoding="utf-8")
    latex = (tmp_path / "probability.tex").read_text(encoding="utf-8")
    policy = loads(
        (tmp_path / "rounding_policy.json").read_text(encoding="utf-8")
    )

    assert "0.123456789012345" in source
    assert "0.1235" in latex
    assert "0.123456789012345" not in latex
    assert policy == {
        "decimal_places": 4,
        "description_pt_br": (
            "Valores numéricos são arredondados apenas nas tabelas LaTeX; "
            "os arquivos CSV preservam a precisão de origem."
        ),
    }


def test_probability_table_has_portuguese_scope_and_uncertainty(
    tmp_path: Path,
) -> None:
    result = _generate(tmp_path)
    latex = result.latex_paths["probability"].read_text(encoding="utf-8")

    assert "Cenário" in latex
    assert "Eventos" in latex
    assert "Denominador" in latex
    assert "IC 95\\%" in latex
    assert "SRPI" in latex
    assert "qualificado" in latex


def test_benchmark_places_confusion_counts_before_derived_metrics(
    tmp_path: Path,
) -> None:
    _generate(tmp_path)
    latex = (tmp_path / "benchmark.tex").read_text(encoding="utf-8")

    assert latex.index("VP") < latex.index("Precisão")
    assert latex.index("FP") < latex.index("Revocação")
    assert latex.index("VN") < latex.index("F1")
    assert latex.index("FN") < latex.index("Taxa de FP")


def test_undefined_benchmark_metric_is_explicit(tmp_path: Path) -> None:
    benchmark = _benchmark().with_columns(
        polars.lit(None, dtype=polars.Float64).alias("precision"),
        polars.lit("No predicted positive observations.").alias(
            "precision_reason"
        ),
    )

    generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=benchmark,
        convergence=_convergence(),
        review=_review(),
    )

    latex = (tmp_path / "benchmark.tex").read_text(encoding="utf-8")
    assert "não definido" in latex


def test_review_separates_analytical_and_causal_columns_and_escapes(
    tmp_path: Path,
) -> None:
    _generate(tmp_path)
    latex = (tmp_path / "technical_review.tex").read_text(encoding="utf-8")

    assert "Evidência analítica" in latex
    assert "Conclusão causal" in latex
    assert "não resolvido" in latex
    assert r"Revisor \& equipe\_1" in latex
    assert r"50\% pendente" in latex


def test_traceability_records_every_source_row(tmp_path: Path) -> None:
    result = _generate(tmp_path)
    trace = polars.read_csv(result.traceability_path)

    assert trace.height == 4
    assert set(trace["source_artifact"]) == {
        "probability.csv",
        "benchmark.csv",
        "convergence.csv",
        "technical_review.csv",
    }
    assert set(trace["generator_version"]) == {"1.2.3"}
    assert set(trace["manuscript_label"]) == {
        "tab:defesa-probabilidade",
        "tab:defesa-benchmark",
        "tab:defesa-convergencia",
        "tab:defesa-revisao-tecnica",
    }
    assert all(trace["row_key"].str.len_chars() > 0)


def test_outputs_are_deterministic_and_existing_targets_are_safe(
    tmp_path: Path,
) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    _generate(first_dir)
    _generate(second_dir)

    assert {path.name: path.read_bytes() for path in first_dir.iterdir()} == {
        path.name: path.read_bytes() for path in second_dir.iterdir()
    }

    with pytest.raises(FileExistsError, match="already exist"):
        _generate(first_dir)
