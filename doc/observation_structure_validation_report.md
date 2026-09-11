# ATP Observation Structure Validation Report

## Current acceptance — 2026-09-10

**Decision:** Accepted for the ten selected SRPI/CRPI files and checks below.
**Reviewer:** Codex, automated comparison with existing ATP transcriptions;
no independent human or electrical review is claimed. This supersedes the
SRPI-only acceptance below and closes the [CRPI findings](crpi_validation_findings.md)
after the separately accepted [parser correction](parser_validation_report.md).

### Scope and acceptance criteria

Inputs: `T_MAN/{SRPI,CRPI}/CASO-COMPLETO/SDEF/case.lis`, at sizes 50, 100,
200, 1,000 and 10,000 in each scenario. Exact input paths, SHA-256 hashes,
source lines and first/last-run references are recorded in the
[SRPI CSV](evidence/parser_audit_checkpoints.csv) and
[CRPI CSV](evidence/parser_crpi_checkpoints.csv). Original inputs remain local
and Git-ignored. References were transcribed directly from printed ATP output
separately from production parsing; their origin and CRPI column positions
are documented in the parser report. Independence concerns the extraction
algorithm, not a second reviewer. First/last runs are purposive checkpoints.

One observation is a scalar phase-to-ground maximum keyed by `source_file`,
`simulation`, `terminal`, and `phase`, with `value_pu` and `time` attributes.
Source paths distinguish equal simulation numbers across files; concatenation
does not renumber runs. Acceptance requires exactly one row for every declared
simulation and combination of `T_MAN`, `1_2LT`, `T_OPO` and A/B/C.
The audit checks the total row count, unique composite-key count and exact
simulation/terminal/phase domains. Extraction assigns one constant source path
per file. Together these conditions imply equality with the complete Cartesian
product: no missing combination can be replaced by a duplicate or extra key.

At each checkpoint, source, simulation, terminal and phase must match, as must
`abs(source_voltage) / 100000.0` and the printed time exactly. The 100,000 V
base is a deterministic audit parameter, not an electrically accepted base.

### Revision and reproduction

Evaluated revision: `a90451eef2271e39d905862734c2d29f4d95132f`.
Production code and the audit script were unchanged for this validation.
The [manifest](evidence/observation_validation_2026-09-10.sha256) identifies
code, schemas, tests, references, execution logs, thesis and dependency lock.
Runtime: Python 3.13.9. No commit or remote code publication is part of this
decision.

Run from the repository root using the existing `uv.lock`:

```bash
rtk proxy sha256sum -c doc/evidence/observation_validation_2026-09-10.sha256
rtk proxy uv run python -m scripts.audit_observation_structure
rtk proxy uv run python -m scripts.audit_observation_structure --checkpoints doc/evidence/parser_crpi_checkpoints.csv
rtk proxy uv run pytest tests/test_preprocessing.py -q
```

Both audits regenerate tables in memory using the corrected parser. Old CRPI
exports and downstream analyses are not accepted here; they require regeneration
and separate validation before reuse.

### Results and decision

| Scenario | Files | Runs | Complete unique observations | Reference voltage/time pairs |
| --- | ---: | ---: | ---: | ---: |
| SRPI | 5 | 11,350 | 102,150 | 30/30 |
| CRPI | 5 | 11,350 | 102,150 | 30/30 |
| Total | 10 | 22,700 | 204,300 | 60/60 |

For each scenario, ascending-size row counts were 450, 900, 1,800, 9,000
and 90,000. All ten input hashes matched. Every simulation contains all nine
terminal/phase combinations, including all three CRPI `T_OPO` phases.
No duplicate keys or checkpoint mismatches were found. Execution records:
[SRPI](evidence/observation_srpi_audit_2026-09-10.txt) and
[CRPI](evidence/observation_crpi_audit_2026-09-10.txt).

All seven preprocessing tests passed, including
`test_load_directory_keeps_files_as_distinct_observation_units`, which checks
24 distinct observations across two source files with equal run identifiers.
The existing parser manifest also passed checksum verification. Software tests
support source-fidelity evidence; passing tests alone is not scientific acceptance.

TCCKL-9 is accepted for this supporting data-structure scope because explicit
observation semantics, exhaustive key completeness within the ten files,
independent numerical checkpoints, provenance and reproduction all agree.
Thesis: `doc/main.tex`, subsection `Escopo e validação do parser`, paragraph
beginning “Observation structure was revalidated”.

The thesis compiled successfully with `latexmk -pdf -interaction=nonstopmode
-file-line-error main.tex` from `doc/` (38 pages). Compilation is a technical
check, not scientific evidence by itself.

### Limitations and reopening

Structural coverage includes A/B/C in every run; independent numerical checks
cover only phase A at first/last runs. This is not an exhaustive numerical
audit, error-rate estimate or confidence interval. Other topologies, scenarios
and ATP layouts require renewed validation. Scalar maxima and occurrence times
do not represent waveforms or establish duration, frequency or oscillatory
content. Electrical P.U. justification remains TCCKL-10; Gaussian adequacy,
statistical independence and physical-versus-numerical interpretation are out
of scope. Reopen if keys, extraction, inputs or layouts invalidate this evidence.

## Historical acceptance — superseded by the current decision


**Validation date:** 2026-09-09  
**Reviewer:** Codex, using independently transcribed ATP source records  
**Preprocessing revision:** `d2b1feb5d039353222d03c7aee3ef10ca8e8b3c2`  
**Decision:** Accepted for the selected structure-validation scope below

## Scope and observation unit

The audit evaluated the five `case.lis` files from the scenario
`T_MAN/SRPI/CASO-COMPLETO/SDEF`, with 50, 100, 200, 1,000, and 10,000 declared
simulations. Their paths and SHA-256 digests are recorded in
[`parser_audit_checkpoints.csv`](evidence/parser_audit_checkpoints.csv).

One observation is one scalar phase-to-ground voltage maximum, keyed by
`source_file`, `simulation`, `terminal`, and `phase`. Its measured attributes
are `value_pu` and `time`. The source-file path identifies the scenario, so
equal simulation numbers in different files remain distinct observations.

For the selected files, completeness requires exactly one row for every
simulation and every combination of terminals `T_MAN`, `1_2LT`, and `T_OPO`
with phases A, B, and C. The four-field observation key must be unique.
Different files are concatenated without renumbering simulations because the
source path is part of that key.

## Independent reference and procedure

The source records were transcribed directly from the ATP text for the first
and last run of each selected file before this audit. They identify the source
line, simulation, phase-A voltage maximum, and maximum time at all three
terminals. The audit verifies each file digest before using those records.

The reproducible comparison is run from the repository root:

```bash
uv run python -m scripts.audit_observation_structure
```

For every selected file, the audit parses the ATP result, creates the
observation table, and checks source-file mapping, simulation coverage,
terminal coverage, phase coverage, key uniqueness, and row completeness. It
then compares the independently transcribed phase-A values and times with the
corresponding rows. Voltage comparison applies the documented transformation
`abs(source_value) / base_voltage` using the explicit audit base of 100,000 V.

## Results

All five hashes and all 30 independently transcribed terminal records matched.
The table contained 102,150 observations: 450, 900, 1,800, 9,000, and 90,000
rows for the five sample sizes. Every four-field key was unique, all declared
simulations were represented, and every simulation contained all nine expected
terminal-phase combinations.

The regression test
`test_load_directory_keeps_files_as_distinct_observation_units` additionally
loads equal simulation identifiers from two scenario paths. It confirms that
the relative source path keeps all 24 rows distinct.

## Supported behavior and limitations

- Acceptance covers the selected scenario and the three stated terminals and
  phases. New scenarios must declare and check their expected layout.
- The audit validates the mapping and deterministic P.U. calculation, not the
  electrical choice of voltage base. That decision remains in TCCKL-10.
- The table stores scalar maxima and their occurrence times. It does not store
  waveforms and cannot support conclusions about transient duration, frequency,
  rate of change, or oscillatory content.
- This validation does not establish whether an extreme is physical or a
  numerical ATP artifact.

## Acceptance decision

TCCKL-9 is accepted as scientifically complete for structuring scalar maxima
from the selected, independently checked ATP cases. The decision is justified
by source hashes, manual source checkpoints, explicit observation semantics,
complete and unique keys, multi-file regression coverage, a reproducible audit,
and documented limitations. The method and scope are recorded in
`doc/main.tex`, subsection `Escopo e validação do parser`.
