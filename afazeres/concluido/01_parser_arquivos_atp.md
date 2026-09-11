# ATP File Parser

## Current status — 2026-09-10

**Concluído.** The CRPI node-column alignment defect is corrected and accepted
for `T_MAN/{SRPI,CRPI}/CASO-COMPLETO/SDEF` at 50, 100, 200, 1,000 and 10,000
runs. This acceptance concerns source-to-model fidelity for the documented
checkpoints. TCCKL-9 remains **Validando** for downstream observations.

### Required evidence before Concluído

- [x] Regression fixture with leading, internal and trailing blank node cells:
  `tests/fixtures/blank_header_cells.txt`; fails before repair, passes after.
- [x] Preserve column positions and compare independent source references:
  [48 ordered CRPI headers](../../doc/evidence/parser_crpi_headers.csv) per
  file and [10 CRPI checkpoints](../../doc/evidence/parser_crpi_checkpoints.csv)
  with signed phase-A maxima/times at three terminals and switch 10 times.
- [x] All five CRPI sizes pass; all historical SRPI checkpoints remain exact.
  Collection scan reconciles 235 files and 533,450 runs. Software gate passes
  100 tests, Ruff and BasedPyright.
- [x] Revision, inputs, procedure, expected/actual results, limitations,
  reviewer, date and decision are recorded in the
  [current report](../../doc/parser_validation_report.md).
  Thesis location: `doc/main.tex`, `Escopo e validação do parser`.

### Provenance and decision

Validation date: 2026-09-10 (America/Sao_Paulo). Reviewer: Codex, using
source transcription independent of production parsing; no second human
reviewer is claimed. Base revision:
`acb91c4dab08f6659ab47dd04b20553860de4d6a` plus the working-tree correction
identified by the [file digest manifest](../../doc/evidence/parser_validation_2026-09-10.sha256).

Accepted: 240 ordered CRPI header comparisons, 20 switching checkpoints and
60 signed maximum/time pairs across both scenarios match the source.
The 235-file scan validates counts, not every column or value independently.
New layouts require renewed validation. This decision does not validate P.U.
bases, physical anomaly causes or downstream observation identity; existing
CRPI artifacts need regeneration and TCCKL-9 validation.

Execution logs: [CRPI](../../doc/evidence/parser_crpi_audit_2026-09-10.txt),
[SRPI](../../doc/evidence/parser_srpi_audit_2026-09-10.txt).

## Historical records — superseded by the current status


## Reopened validation — 2026-09-10

**Validando.** CRPI header alignment must be corrected and independently
validated under TCCKL-8. `_parse_variable_headers` discards empty column
positions when splitting the node line, shifting node-to-variable mappings.
The previous SRPI checkpoints remain historical evidence; the collection-wide
count scan did not establish column fidelity for every layout.

Evidence: [CRPI findings](../../doc/crpi_validation_findings.md).

### Required evidence before Concluído

- [ ] Add a regression fixture with leading and internal blank node cells.
- [ ] Preserve column positions and compare CRPI headers, signed maxima, and
  times with independently transcribed `.lis` records.
- [ ] Recheck all five CRPI sizes and preserve the accepted SRPI checkpoints.
- [ ] Record revision, inputs, results, limitations, reviewer, acceptance date,
  decision, and corresponding thesis location before closing again.

The correction belongs here; TCCKL-9 validates the resulting observations.

## Historical record (superseded current status)

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
