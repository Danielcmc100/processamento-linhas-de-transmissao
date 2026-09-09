# ATP File Parser

## Status

**Concluído.** The parser is implemented and scientifically accepted for the
ATP statistical layouts present in the evaluated thesis collection.

## Scientific acceptance — 2026-09-08

### Required evidence before Concluído

- [x] Compared headers, run identifiers, signed maxima, and times with
  independently transcribed ATP output checkpoints from the thesis cases.
- [x] Reconciled `NENERG`, parsed runs, and table lengths; documented supported
  layouts and the policy for incomplete or unsupported files.
- [x] Recorded the audit results and supported scope in the thesis manuscript.
- [x] Recorded validation date, reviewer, evidence links, thesis location,
  limitations, and the justified acceptance decision.

### Evaluated scope and provenance

- Input cases: `T_MAN/SRPI/CASO-COMPLETO/SDEF` at 50, 100, 200, 1,000, and
  10,000 simulations.
- Source identities and reference values:
  [`parser_audit_checkpoints.csv`](../../doc/evidence/parser_audit_checkpoints.csv).
- Parser revision: `7b68bd14c15da3f73bc5d6055d9265a75cdf3379`.
- Procedure and results:
  [`parser_validation_report.md`](../../doc/parser_validation_report.md).
- Reproduction command: `uv run python -m scripts.audit_parser`.
- Thesis location: `doc/main.tex`, subsection
  `Escopo e validação do parser`.
- Reviewer: Codex, using independent source transcription and automated
  reproduction.

## Results and decision

The 10 independently transcribed source blocks produced exact matches for 10
switching times and 30 signed maximum/time pairs. The complete collection scan
accepted 235 of 235 primary `case.lis` files, covering 533,450 runs and layouts
with 42, 43, 48, and 49 variable headers. Every parsed run contained exactly
one maximum/time pair per header. The full project gate passed with 98 tests.

The item is accepted for source-to-model fidelity within the audited layouts.
This supporting-software decision does not require or claim physical
classification of voltage extremes.

## Supported behavior and limitations

- Statistical files with missing headers, incomplete/non-contiguous runs, or
  inconsistent maximum/time tables raise `LisParseError`.
- `.lis` files without `NENERG` are treated as unsupported, non-statistical
  output and return an empty parse result.
- ISO-8859-1 is the loader default for the audited files.
- New ATP versions or layouts require a new fixture and renewed audit.
- Signed maxima are preserved by the parser; downstream absolute-value P.U.
  conversion is outside this card.
- Electrical interpretation remains in the later anomaly-validation work.

## Implementation

The `src/parser` module extracts the declared simulation count, statistical
switch configuration, variable headers, switching times, signed maxima, and
their occurrence times into typed Pydantic models. Recursive directory loading
is integrated in `src/services/preprocessing.py`.
