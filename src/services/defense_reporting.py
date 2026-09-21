"""Generate traceable machine and manuscript thesis-defense tables."""

from __future__ import annotations

from csv import writer
from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import Enum
from json import dumps
from pathlib import Path
from typing import Mapping

from polars import DataFrame

_ROUNDING_DESCRIPTION = (
    "Valores numéricos são arredondados apenas nas tabelas LaTeX; "
    "os arquivos CSV preservam a precisão de origem."
)


@dataclass(frozen=True, slots=True)
class RoundingPolicy:
    """Presentation-only decimal rounding policy."""

    decimal_places: int = 3

    def __post_init__(self) -> None:
        """Reject unsupported presentation precision."""
        if not 0 <= self.decimal_places <= 15:
            raise ValueError("decimal_places must be between 0 and 15.")


@dataclass(frozen=True, slots=True)
class DefenseReportingResult:
    """Paths produced by one defense-table generation."""

    source_paths: dict[str, Path]
    latex_paths: dict[str, Path]
    traceability_path: Path
    rounding_policy_path: Path


@dataclass(frozen=True, slots=True)
class _TableDefinition:
    """Required fields and Portuguese presentation for one table."""

    name: str
    source_filename: str
    latex_filename: str
    required_columns: tuple[str, ...]
    display_columns: tuple[tuple[str, str], ...]
    key_columns: tuple[str, ...]
    sort_columns: tuple[str, ...]
    caption: str
    manuscript_label: str


_DEFINITIONS = (
    _TableDefinition(
        name="probability",
        source_filename="probability.csv",
        latex_filename="probability.tex",
        required_columns=(
            "scenario",
            "sample_size",
            "terminal",
            "phase",
            "event_definition",
            "threshold",
            "occurrence_count",
            "denominator",
            "empirical_probability",
            "confidence_interval_lower",
            "confidence_interval_upper",
            "validation_status",
        ),
        display_columns=(
            ("scenario", "Cenário"),
            ("sample_size", "N"),
            ("terminal", "Terminal"),
            ("phase", "Fase"),
            ("occurrence_count", "Eventos"),
            ("denominator", "Denominador"),
            ("empirical_probability", "Probabilidade"),
            ("confidence_interval_lower", "IC 95\\% inferior"),
            ("confidence_interval_upper", "IC 95\\% superior"),
            ("validation_status", "Status"),
        ),
        key_columns=(
            "scenario",
            "sample_size",
            "terminal",
            "phase",
            "threshold",
        ),
        sort_columns=("scenario", "sample_size", "terminal", "phase"),
        caption="Probabilidade empírica de excedência por grupo.",
        manuscript_label="tab:defesa-probabilidade",
    ),
    _TableDefinition(
        name="benchmark",
        source_filename="benchmark.csv",
        latex_filename="benchmark.tex",
        required_columns=(
            "intervention_family",
            "intervention_intensity",
            "method",
            "true_positive",
            "false_positive",
            "true_negative",
            "false_negative",
            "precision",
            "recall",
            "f1",
            "false_positive_rate",
            "precision_reason",
            "recall_reason",
            "f1_reason",
            "false_positive_rate_reason",
        ),
        display_columns=(
            ("intervention_family", "Intervenção"),
            ("intervention_intensity", "Intensidade"),
            ("method", "Método"),
            ("true_positive", "VP"),
            ("false_positive", "FP"),
            ("true_negative", "VN"),
            ("false_negative", "FN"),
            ("precision", "Precisão"),
            ("recall", "Revocação"),
            ("f1", "F1"),
            ("false_positive_rate", "Taxa de FP"),
        ),
        key_columns=(
            "intervention_family",
            "intervention_intensity",
            "method",
        ),
        sort_columns=(
            "intervention_family",
            "intervention_intensity",
            "method",
        ),
        caption="Desempenho nos ensaios com perturbações controladas.",
        manuscript_label="tab:defesa-benchmark",
    ),
    _TableDefinition(
        name="convergence",
        source_filename="convergence.csv",
        latex_filename="convergence.tex",
        required_columns=(
            "scenario",
            "sample_size",
            "terminal",
            "phase",
            "mean",
            "percentile_95",
            "empirical_probability",
            "confidence_interval_width",
            "fitted_model_status",
            "candidate_count",
            "candidate_rate",
            "grouping_policy",
            "method_policy",
            "comparison_status",
        ),
        display_columns=(
            ("scenario", "Cenário"),
            ("sample_size", "N"),
            ("terminal", "Terminal"),
            ("phase", "Fase"),
            ("mean", "Média"),
            ("percentile_95", "Percentil 95"),
            ("empirical_probability", "Probabilidade"),
            ("confidence_interval_width", "Largura do IC"),
            ("fitted_model_status", "Ajuste"),
            ("candidate_count", "Candidatos"),
            ("candidate_rate", "Taxa de candidatos"),
            ("comparison_status", "Status"),
        ),
        key_columns=(
            "scenario",
            "sample_size",
            "terminal",
            "phase",
            "grouping_policy",
            "method_policy",
        ),
        sort_columns=("scenario", "sample_size", "terminal", "phase"),
        caption="Convergência das evidências entre tamanhos de amostra.",
        manuscript_label="tab:defesa-convergencia",
    ),
    _TableDefinition(
        name="technical_review",
        source_filename="technical_review.csv",
        latex_filename="technical_review.tex",
        required_columns=(
            "source_file",
            "source_sha256",
            "simulation",
            "terminal",
            "phase",
            "source_value",
            "value_pu",
            "method_evidence",
            "conclusion",
            "reviewer",
            "review_date",
            "rationale",
        ),
        display_columns=(
            ("source_file", "Fonte"),
            ("simulation", "Simulação"),
            ("terminal", "Terminal"),
            ("phase", "Fase"),
            ("source_value", "Valor com sinal"),
            ("value_pu", "Valor em p.u."),
            ("method_evidence", "Evidência analítica"),
            ("conclusion", "Conclusão causal"),
            ("reviewer", "Revisor"),
            ("review_date", "Data"),
            ("rationale", "Justificativa"),
        ),
        key_columns=(
            "source_sha256",
            "simulation",
            "terminal",
            "phase",
        ),
        sort_columns=(
            "source_file",
            "simulation",
            "terminal",
            "phase",
        ),
        caption="Revisão técnica dos casos selecionados.",
        manuscript_label="tab:defesa-revisao-tecnica",
    ),
)


def generate_defense_tables(
    output_dir: Path,
    *,
    probability: DataFrame,
    benchmark: DataFrame,
    convergence: DataFrame,
    review: DataFrame,
    rounding: RoundingPolicy = RoundingPolicy(),
    generator_version: str = "1.0.0",
    manuscript_labels: Mapping[str, str] | None = None,
    overwrite: bool = False,
) -> DefenseReportingResult:
    """Write four source CSVs, four Portuguese LaTeX tables, and manifests.

    CSV serialization uses source scalar precision. Rounding affects only
    LaTeX presentation. All known targets are checked before any write.

    Returns:
        Paths grouped by artifact role.

    Raises:
        FileExistsError: If a target exists and overwrite is disabled.
        ValueError: If a source table lacks required evidence.
    """
    if not generator_version:
        raise ValueError("generator_version must not be empty.")
    tables = {
        "probability": probability,
        "benchmark": benchmark,
        "convergence": convergence,
        "technical_review": review,
    }
    definitions = {
        definition.name: _with_label(definition, manuscript_labels)
        for definition in _DEFINITIONS
    }
    for name, table in tables.items():
        _validate_table(table, definitions[name])

    source_paths = {
        name: output_dir / definition.source_filename
        for name, definition in definitions.items()
    }
    latex_paths = {
        name: output_dir / definition.latex_filename
        for name, definition in definitions.items()
    }
    traceability_path = output_dir / "table_traceability.csv"
    rounding_path = output_dir / "rounding_policy.json"
    targets = (
        *source_paths.values(),
        *latex_paths.values(),
        traceability_path,
        rounding_path,
    )
    conflicts = [path for path in targets if path.exists()]
    if conflicts and not overwrite:
        names = ", ".join(path.name for path in conflicts)
        message = f"Defense table artifacts already exist: {names}."
        raise FileExistsError(message)

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_rows: list[dict[str, object]] = []
    for name, definition in definitions.items():
        table = tables[name].sort(list(definition.sort_columns))
        _write_machine_csv(source_paths[name], table)
        latex_paths[name].write_text(
            _render_latex(table, definition, rounding),
            encoding="utf-8",
        )
        trace_rows.extend(_trace_rows(table, definition, generator_version))

    _write_rows_csv(
        traceability_path,
        (
            "table_name",
            "source_artifact",
            "row_key",
            "generator_version",
            "manuscript_label",
        ),
        trace_rows,
    )
    rounding_path.write_text(
        dumps(
            {
                "decimal_places": rounding.decimal_places,
                "description_pt_br": _ROUNDING_DESCRIPTION,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return DefenseReportingResult(
        source_paths=source_paths,
        latex_paths=latex_paths,
        traceability_path=traceability_path,
        rounding_policy_path=rounding_path,
    )


def _with_label(
    definition: _TableDefinition,
    labels: Mapping[str, str] | None,
) -> _TableDefinition:
    """Apply an optional manuscript label without changing other metadata."""
    if labels is None or definition.name not in labels:
        return definition
    label = labels[definition.name]
    if not label:
        raise ValueError(f"Manuscript label for {definition.name} is empty.")
    return replace(definition, manuscript_label=label)


def _validate_table(table: DataFrame, definition: _TableDefinition) -> None:
    """Require every source and presentation field before writing."""
    missing = [
        column for column in definition.required_columns if column not in table
    ]
    if missing:
        raise ValueError(
            f"Missing {definition.name} columns: {', '.join(missing)}."
        )


def _write_machine_csv(path: Path, table: DataFrame) -> None:
    """Write all source columns without presentation rounding."""
    rows = [dict(row) for row in table.iter_rows(named=True)]
    _write_rows_csv(path, tuple(table.columns), rows)


def _write_rows_csv(
    path: Path,
    columns: tuple[str, ...],
    rows: list[dict[str, object]],
) -> None:
    """Write deterministic UTF-8 CSV with canonical complex values."""
    with path.open("w", encoding="utf-8", newline="") as target:
        csv_writer = writer(target, lineterminator="\n")
        csv_writer.writerow(columns)
        for row in rows:
            csv_writer.writerow([
                _machine_value(row.get(column)) for column in columns
            ])


def _machine_value(value: object) -> object:
    """Preserve scalars and canonically serialize structured values."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (dict, list, tuple)):
        return dumps(
            value,
            default=_json_default,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    return value


def _json_default(value: object) -> object:
    """Serialize supported nested review values."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    raise TypeError(f"Unsupported structured evidence value: {type(value)!r}.")


def _render_latex(
    table: DataFrame,
    definition: _TableDefinition,
    rounding: RoundingPolicy,
) -> str:
    """Render one deterministic Brazilian Portuguese LaTeX table."""
    columns = definition.display_columns
    alignment = "l" * len(columns)
    header = " & ".join(label for _, label in columns) + r" \\"
    lines = [
        "% Tabela gerada automaticamente.",
        f"% Política de arredondamento: {rounding.decimal_places} casas "
        "decimais apenas nesta apresentação.",
        r"\begin{table}[htbp]",
        r"\centering",
        f"\\caption{{{_latex_escape(definition.caption)}}}",
        f"\\label{{{definition.manuscript_label}}}",
        f"\\begin{{tabular}}{{{alignment}}}",
        r"\hline",
        header,
        r"\hline",
    ]
    for row in table.iter_rows(named=True):
        values = [
            _presentation_value(row[column], column, rounding)
            for column, _ in columns
        ]
        lines.append(" & ".join(values) + " \\\\")
    lines.extend((r"\hline", r"\end{tabular}", r"\end{table}", ""))
    return "\n".join(lines)


def _presentation_value(
    value: object,
    column: str,
    rounding: RoundingPolicy,
) -> str:
    """Format and safely escape one presentation value."""
    if value is None:
        return "não definido"
    if isinstance(value, bool):
        return "sim" if value else "não"
    if isinstance(value, float):
        return f"{value:.{rounding.decimal_places}f}"
    translated = _translate_value(str(_machine_value(value)), column)
    return _latex_escape(translated)


def _translate_value(value: str, column: str) -> str:
    """Translate controlled statuses while preserving technical identities."""
    translations = {
        "qualified": "qualificado",
        "valid": "válido",
        "invalid": "inválido",
        "comparable": "comparável",
        "incomplete": "incompleto",
        "not_rejected": "não rejeitado",
        "rejected": "rejeitado",
        "descriptive_only": "somente descritivo",
        "unresolved": "não resolvido",
        "data defect": "defeito de dados",
        "suspected numerical artifact": "artefato numérico suspeito",
        "physically plausible extreme": "extremo fisicamente plausível",
    }
    if column in {
        "validation_status",
        "comparison_status",
        "fitted_model_status",
        "conclusion",
    }:
        return translations.get(value, value)
    return value


def _latex_escape(value: str) -> str:
    """Escape user and source text for a LaTeX table cell."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(
        replacements.get(character, character) for character in value
    )


def _trace_rows(
    table: DataFrame,
    definition: _TableDefinition,
    generator_version: str,
) -> list[dict[str, object]]:
    """Build one traceability entry per source row."""
    return [
        {
            "table_name": definition.name,
            "source_artifact": definition.source_filename,
            "row_key": "|".join(
                str(_machine_value(row[column]))
                for column in definition.key_columns
            ),
            "generator_version": generator_version,
            "manuscript_label": definition.manuscript_label,
        }
        for row in table.iter_rows(named=True)
    ]
