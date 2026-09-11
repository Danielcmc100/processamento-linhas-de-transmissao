# ATP Statistical Parser Validation Report

## Current acceptance — 2026-09-10

**Reviewer:** Codex (source transcription and automated comparison; no
independent human review is claimed). **Decision:** Accepted for the ten
selected SRPI/CRPI files and the specific checks below. This supersedes the
broader historical acceptance, reopened after the
[CRPI findings](crpi_validation_findings.md).

### Revision and reproduction

Base revision: `acb91c4dab08f6659ab47dd04b20553860de4d6a`, plus the local
TCCKL-8 correction. The evaluated working-tree files and dependency lock are
identified by [SHA-256 manifest](evidence/parser_validation_2026-09-10.sha256).
No new Git commit or remote publication is made by this validation.

Run from the repository root with the existing `uv.lock` (Python 3.13.9):

```bash
rtk proxy sha256sum -c doc/evidence/parser_validation_2026-09-10.sha256
rtk proxy uv run python -m scripts.audit_parser
rtk proxy uv run python -m scripts.audit_parser --checkpoints doc/evidence/parser_crpi_checkpoints.csv
rtk proxy uv run task format
rtk proxy uv run task lint
rtk proxy uv run task test
rtk proxy uv run task typecheck
```

### Reference, scope and acceptance criteria

Inputs are `T_MAN/{SRPI,CRPI}/CASO-COMPLETO/SDEF/case.lis` at 50, 100,
200, 1,000 and 10,000 simulations. Full relative paths and input digests are
in the unchanged [SRPI references](evidence/parser_audit_checkpoints.csv)
and new [CRPI references](evidence/parser_crpi_checkpoints.csv).
The complete original files remain local, Git-ignored thesis inputs.

CRPI was selected because it exposed the defect, before testing the repair.
The reference is direct transcription from printed ATP records, not parser
output. All 48 variable/node pairs were transcribed in their original order
from lines 1,784--1,797 into
[header references](evidence/parser_crpi_headers.csv). The first source block
is retained as a line-numbered [excerpt](evidence/parser_crpi_source_excerpt.txt).
For each file, the first and last runs were inspected at the CSV source lines.
Phase-A ground maxima occupy one-based columns 16 (`T_MANA`), 20 (`1_2LTA`)
and 22 (`T_OPOA`). Reference angle is not a variable column. Switch 10 and
the corresponding signed values and times were copied directly from these
records. References were prepared separately from production parsing.

Acceptance requires exact equality at printed precision: all ordered CRPI
headers, every selected signed maximum/time pair and switching checkpoint,
matching file digests, declared/parsed run counts, contiguous identifiers,
and one maximum/time pair per header in every parsed run. The same reviewer
prepared and executed the audit; independence here means independence from
the production extraction algorithm, not a second reviewer.

### Correction and results

The parser now slices the node row at the variable-column positions instead
of splitting away empty cells. The synthetic regression fixture
`tests/fixtures/blank_header_cells.txt` includes leading, internal and
trailing blanks and a reference-angle prefix. It failed before the correction
(`T_OPOA` incorrectly received `T_MANC`) and passed afterwards. Its reduced
column sequence is synthetic and is not presented as a complete ATP case.
The `.txt` suffix keeps it outside recursive `.lis` loader fixture scans.

| Check | Result |
| --- | --- |
| CRPI inputs | All five hashes match; 11,350 runs total |
| CRPI ordered headers | 48 pairs per file, 240 comparisons, no mismatch |
| CRPI first/last checkpoints | 10 switch times and 30 signed maximum/time pairs match |
| Retained SRPI checkpoints | 10 switch times and 30 signed maximum/time pairs match |
| Complete collection scan | 235 files, 533,450 runs, 20 size/header combinations |
| Software gate | Ruff passes; 100 tests pass; BasedPyright reports no errors or warnings |

The scan checks completeness and table lengths for the available collection;
it does **not** independently verify every column or numerical value in those
235 files. Saved execution output:
[CRPI](evidence/parser_crpi_audit_2026-09-10.txt) and
[SRPI](evidence/parser_srpi_audit_2026-09-10.txt).

### Decision, limitations and thesis traceability

The evidence closes the reopened alignment defect within the stated
source-checkpoint scope. This is supporting-software validation of source
fidelity and reproducibility within the evaluated scope.
It is not a statistical estimate of the parser error rate: selected first/last
runs are purposive checkpoints, not a random sample or confidence interval.
Other topologies, ATP versions and layouts need new independent checkpoints.
No claim of exhaustive numerical agreement beyond the sampled values is made.

Missing or inconsistent statistical tables continue to raise `LisParseError`;
files without `NENERG` remain unsupported and return empty results. Signed
values are retained. P.U. bases, anomaly causes and downstream observation
acceptance remain outside this decision. Previously generated CRPI artifacts
must be regenerated and validated under TCCKL-9 before downstream use;
TCCKL-9 remains **Validando**.

Thesis location: `doc/main.tex`, subsection `Escopo e validação do parser`.
The updated subsection records the defect, method, evaluated scope and limits.

## Historical acceptance — superseded by the current decision

**Validation date:** 2026-09-08  
**Reviewer:** Codex, using an independent source transcription and automated
reproduction  
**Parser revision:** `7b68bd14c15da3f73bc5d6055d9265a75cdf3379`  
**Decision:** Accepted for the supported extraction scope stated below

## Scope and source data

The audit evaluated the main statistical `case.lis` files under
`input_files/casos/`. These files are local thesis inputs and are intentionally
excluded from Git. The five independently checked files use the scenario
`T_MAN/SRPI/CASO-COMPLETO/SDEF` at 50, 100, 200, 1,000, and 10,000 declared
simulations. Their exact paths and SHA-256 digests are recorded in
[`parser_audit_checkpoints.csv`](evidence/parser_audit_checkpoints.csv).

The five files were selected before parsing because they hold the topology,
switching policy, complete equivalent-network case, and no-pre-insertion-
resistor scenario used by the saved sample-size analyses. This validates
parser fidelity for that study path; it does not validate the electrical
interpretation of those simulations.

## Independent reference and procedure

The expected values in the checkpoint CSV were transcribed directly from the
ATP text, without calling production parser functions. For each selected file,
the first and last simulation blocks were inspected at the recorded source
line. Each checkpoint records the run identifier, switch 10 time, and the
signed phase-A maximum and maximum time at `T_MAN`, `1_2LT`, and `T_OPO`.
The variable positions were established from the source header block at lines
1,768--1,783 of each file.

The reproducible comparison was then run from the repository root:

```bash
uv run python -m scripts.audit_parser
```

The audit checks each file digest before comparing values. It also reconciles
the declared `NENERG`, parsed run count, contiguous run identifiers, header
count, and maximum/time pair count. Finally, it parses every main statistical
`case.lis` file to test all layouts currently present in the thesis input
collection.

## Results

All five file hashes matched the recorded sources. All 10 independently
transcribed simulation blocks matched exactly: 10 switch times and 30 signed
maximum/time pairs. No sign or time disagreement was observed.

The complete scan accepted all 235 primary statistical files and 533,450
simulation runs. Every run had one maximum/time pair per parsed header. The
observed layout matrix was identical at every sample size:

| `NENERG` | 42 headers | 43 headers | 48 headers | 49 headers | Files |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 5 | 18 | 6 | 18 | 47 |
| 100 | 5 | 18 | 6 | 18 | 47 |
| 200 | 5 | 18 | 6 | 18 | 47 |
| 1,000 | 5 | 18 | 6 | 18 | 47 |
| 10,000 | 5 | 18 | 6 | 18 | 47 |

Software regression checks additionally demonstrated that a statistical file
is rejected when its declared run count, header block, or maximum/time table
is incomplete. The full project gate passed with 98 tests on the validation
date.

## Supported behavior and limitations

The accepted scope is ATP statistical-overvoltage output using the markers
present in the audited collection: `NENERG`, `otherwise blank space`,
`Random switching times for simulation number`, optional first-run table-dump
text, and `Times of maxima`. Files are decoded as ISO-8859-1 by the loaders.

- A statistical block with missing headers, missing/non-contiguous runs, or
  inconsistent maximum/time counts raises `LisParseError`; partial data is not
  silently returned.
- A `.lis` file without an `NENERG` declaration is treated as unsupported,
  non-statistical output and returns an empty parse result. This allows the
  directory loader to ignore deterministic `shot*.lis` files.
- The audit covers the 235 primary files currently available. A new ATP
  version or layout requires a new regression fixture and renewed audit.
- The parser preserves signed maxima. Downstream P.U. preprocessing applies an
  absolute value; that transformation is outside this card's acceptance.
- This validation establishes source-to-model fidelity. It does not determine
  whether an extreme is a physical event or a numerical ATP artifact.

## Acceptance decision

TCCKL-8 is accepted as scientifically complete for syntactic extraction of
the audited ATP statistical layouts. Acceptance is justified by independent
source checkpoints, exhaustive reconciliation of the available primary files,
explicit failure behavior, reproducible inputs, and regression tests. The
method and its limits are recorded in `doc/main.tex`, subsection
`Escopo e validação do parser`. Electrical interpretation remains assigned to
the later anomaly-validation work and does not block this parser decision.
