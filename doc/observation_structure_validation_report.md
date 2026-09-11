# ATP Observation Structure Validation Report

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
