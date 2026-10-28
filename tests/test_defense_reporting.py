"""Tests for traceable thesis-defense source and LaTeX tables."""

from json import loads
from pathlib import Path

from polars import (
    DataFrame,
    Float64,
    Int64,
    String,
    col,
    concat,
    lit,
    read_csv,
)
from pytest import raises

from src.services.defense_reporting import (
    DefenseReportingResult,
    RoundingPolicy,
    generate_defense_tables,
)


def _probability() -> DataFrame:
    return DataFrame({
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


def _benchmark() -> DataFrame:
    return DataFrame({
        "intervention_family": ["point"],
        "requested_contamination_rate": [0.1],
        "effective_contamination_rate": [0.1],
        "row_count": [17],
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


def _convergence() -> DataFrame:
    return DataFrame({
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


def _review() -> DataFrame:
    return DataFrame({
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


def _review_sources() -> DataFrame:
    return DataFrame({
        "scenario": ["SRPI"],
        "sample_size": [1000],
        "source_path": ["1000-simulacoes/SRPI/caso_1.lis"],
        "source_sha256": ["abc123"],
    })


def _generate(output_dir: Path) -> DefenseReportingResult:
    return generate_defense_tables(
        output_dir,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=_review(),
        review_sources=_review_sources(),
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
    assert "0,1235" in latex
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
        lit(None, dtype=Float64).alias("precision"),
        lit("No predicted positive observations.").alias("precision_reason"),
    )

    generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=benchmark,
        convergence=_convergence(),
        review=_review(),
        review_sources=_review_sources(),
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
    trace = read_csv(result.traceability_path)

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

    with raises(FileExistsError, match="already exist"):
        _generate(first_dir)


def test_tables_paginate_and_wrap_within_landscape_width(
    tmp_path: Path,
) -> None:
    result = _generate(tmp_path)
    for path in result.latex_paths.values():
        latex = path.read_text(encoding="utf-8")
        assert r"\begin{landscape}" in latex
        assert r"\begin{longtable}" in latex
        assert r"\linewidth-2\tabcolsep" in latex
        assert r"\endfirsthead" in latex
        assert r"\endhead" in latex
        assert r"\begin{table}" not in latex


def test_localized_numbers_preserve_raw_values_and_source_identity(
    tmp_path: Path,
) -> None:
    """Localize numeric measures without changing identifiers or CSVs."""
    result = _generate(tmp_path)
    convergence = result.latex_paths["convergence"].read_text()
    review = result.latex_paths["technical_review"].read_text()

    assert "10.000" in convergence
    assert "1,8765" in convergence
    assert "-245.000,1235" in review
    assert r"caso\_1.lis" in review
    assert "2026-09-21" in review
    assert (
        "-245000.123456" in result.source_paths["technical_review"].read_text()
    )
    assert "10000" in result.source_paths["convergence"].read_text()


def test_benchmark_condition_identity_and_metrics_survive_rendering(
    tmp_path: Path,
) -> None:
    """Distinguish contamination at fixed intensity and preserve metrics."""
    benchmark = concat([
        _benchmark().with_columns(
            lit(rate).alias("requested_contamination_rate"),
            lit(rate).alias("effective_contamination_rate"),
        )
        for rate in (0.01, 0.05, 0.1)
    ])
    result = generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=benchmark,
        convergence=_convergence(),
        review=_review(),
        review_sources=_review_sources(),
        rounding=RoundingPolicy(decimal_places=4),
    )
    latex = result.latex_paths["benchmark"].read_text()
    trace = read_csv(result.traceability_path).filter(
        col("table_name") == "benchmark"
    )
    assert trace["row_key"].n_unique() == 3
    assert "Contaminação solicitada" in latex
    assert "Contaminação efetiva" in latex
    assert "N aval." in latex
    for percentage in ("1", "5", "10"):
        assert f"{percentage}\\%" in latex
    rows = [line for line in latex.splitlines() if "pontual &" in line]
    assert len(rows) == 3
    for row in rows:
        assert " & 1,5000 & " in row
        assert " & 17 & 4 & 1 & 10 & 2 & " in row
        assert "0,8000 & 0,6667 & 0,7273 & 0,0909" in row
    assert "point" not in latex
    saved = read_csv(result.source_paths["benchmark"])
    assert saved.equals(
        benchmark.sort([
            "intervention_family",
            "intervention_intensity",
            "method",
        ])
    )


def test_review_duplicate_basenames_controls_and_pending_status(
    tmp_path: Path,
) -> None:
    """Resolve duplicate basenames and retain case evidence and status."""
    review = concat([
        _review(),
        _review().with_columns(
            lit("def456").alias("source_sha256"),
            lit("").alias("method_evidence"),
        ),
    ])
    sources = concat([
        _review_sources(),
        _review_sources().with_columns(
            lit("CRPI").alias("scenario"),
            lit(200, dtype=Int64).alias("sample_size"),
            lit("200-simulacoes/CRPI/caso_1.lis").alias("source_path"),
            lit("def456").alias("source_sha256"),
        ),
    ])
    result = generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=review,
        review_sources=sources,
        rounding=RoundingPolicy(decimal_places=4),
    )
    latex = result.latex_paths["technical_review"].read_text()
    assert "SRPI-1000" in latex and "CRPI-200" in latex
    assert "1000-simulacoes/SRPI/caso_1.lis" in latex
    assert "200-simulacoes/CRPI/caso_1.lis" in latex
    assert "abc123" in latex and "def456" in latex
    assert "controle sem sinalização" in latex
    assert "aguardando revisão elétrica" in latex
    assert latex.count("não resolvido") == 1
    assert latex.count(r"Revisor \& equipe\_1") == 1
    assert latex.count("-245.000,1235") == 2
    assert latex.count("2,1744") == 2
    saved = read_csv(
        result.source_paths["technical_review"],
        missing_utf8_is_empty_string=True,
    )
    assert saved.equals(review)


def test_review_missing_source_identity_blocks_publication(
    tmp_path: Path,
) -> None:
    """Reject review records absent from the authoritative source catalog."""
    with raises(ValueError, match="review source identity"):
        generate_defense_tables(
            tmp_path,
            probability=_probability(),
            benchmark=_benchmark(),
            convergence=_convergence(),
            review=_review(),
            review_sources=_review_sources().head(0),
        )
    assert not list(tmp_path.iterdir())


def test_review_ambiguous_source_identity_blocks_publication(
    tmp_path: Path,
) -> None:
    """Reject one hash assigned to conflicting source identities."""
    sources = concat([
        _review_sources(),
        _review_sources().with_columns(
            lit("different/caso_1.lis").alias("source_path")
        ),
    ])
    with raises(ValueError, match="review source identity"):
        generate_defense_tables(
            tmp_path,
            probability=_probability(),
            benchmark=_benchmark(),
            convergence=_convergence(),
            review=_review(),
            review_sources=sources,
        )
    assert not list(tmp_path.iterdir())


def test_review_distinct_statuses_remain_per_case(tmp_path: Path) -> None:
    """Collapse shared notes only when every case has the same value."""
    review = concat([
        _review(),
        _review().with_columns(
            lit(8).cast(Int64).alias("simulation"),
            lit("data defect").alias("conclusion"),
            lit("Outro revisor").alias("reviewer"),
        ),
    ])
    result = generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=review,
        review_sources=_review_sources(),
    )
    latex = result.latex_paths["technical_review"].read_text()
    assert "não resolvido" in latex
    assert "defeito de dados" in latex
    assert "Outro revisor" in latex
    assert r"Revisor \& equipe\_1" in latex


def test_review_null_control_evidence_is_explicit(tmp_path: Path) -> None:
    """CSV-null empty evidence retains the non-signaled control identity."""
    result = generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=_review().with_columns(
            lit(None, dtype=String).alias("method_evidence")
        ),
        review_sources=_review_sources(),
    )
    latex = result.latex_paths["technical_review"].read_text()
    assert "controle sem sinalização" in latex


def test_review_basename_only_catalog_blocks_publication(
    tmp_path: Path,
) -> None:
    """A catalog basename cannot substitute for a full source path."""
    with raises(ValueError, match="review source identity"):
        generate_defense_tables(
            tmp_path,
            probability=_probability(),
            benchmark=_benchmark(),
            convergence=_convergence(),
            review=_review(),
            review_sources=_review_sources().with_columns(
                lit("caso_1.lis").alias("source_path")
            ),
        )
    assert not list(tmp_path.iterdir())


def test_review_shared_hash_resolves_with_explicit_context(
    tmp_path: Path,
) -> None:
    """Identical source bytes can belong to distinct experimental contexts."""
    sources = concat([
        _review_sources(),
        _review_sources().with_columns(
            lit("CRPI").alias("scenario"),
            lit("1000-simulacoes/CRPI/caso_1.lis").alias("source_path"),
        ),
    ])
    review = concat([
        _review().with_columns(
            lit(scenario).alias("scenario"),
            lit(1000).alias("sample_size"),
        )
        for scenario in ("SRPI", "CRPI")
    ])
    result = generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=review,
        review_sources=sources,
    )
    latex = result.latex_paths["technical_review"].read_text()
    assert "SRPI-1000" in latex and "CRPI-1000" in latex
    assert "1000-simulacoes/SRPI/caso_1.lis" in latex
    assert "1000-simulacoes/CRPI/caso_1.lis" in latex
    assert latex.count("abc123") == 2


def test_review_context_participates_in_traceability(tmp_path: Path) -> None:
    """Trace keys distinguish identical bytes in different scenarios."""
    sources = concat([
        _review_sources(),
        _review_sources().with_columns(lit("CRPI").alias("scenario")),
    ])
    review = concat([
        _review().with_columns(
            lit(scenario).alias("scenario"),
            lit(1000).alias("sample_size"),
        )
        for scenario in ("SRPI", "CRPI")
    ])
    result = generate_defense_tables(
        tmp_path,
        probability=_probability(),
        benchmark=_benchmark(),
        convergence=_convergence(),
        review=review,
        review_sources=sources,
    )
    trace = read_csv(result.traceability_path).filter(
        col("table_name") == "technical_review"
    )
    assert trace["row_key"].n_unique() == 2
