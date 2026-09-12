# Data validation and cleaning acceptance — TCCKL-11

## Decision and evaluated scope

**Date:** 2026-09-11. **Reviewer:** Codex, automated source comparison and
adversarial verification; no independent human or electrical review is claimed.
**Decision:** Accepted for measurement integrity in the ten complete-model,
no-defect SRPI/CRPI cases previously accepted under TCCKL-8/9/10. This supporting
validation does not require a Gaussian hypothesis or classify physical causes.

The scope is `T_MAN/{SRPI,CRPI}/CASO-COMPLETO/SDEF/case.lis` at 50, 100,
200, 1,000 and 10,000 runs, terminals T_MAN, 1_2LT and T_OPO, phases A/B/C.
The audit uses the accepted base of 112677 V. The cases are evaluated separately;
the aggregate counts below do not assert independence between sample-size files.

Revision: working tree based on `4ef45fee2f71ba2fe39f6f467a2c183b9f70f1e7`,
with the validation, pipeline, reporting and audit changes identified by
[evidence/cleaning_validation.sha256](evidence/cleaning_validation.sha256).
The manifest records exact evaluated bytes; no commit or publication is claimed.

## Declared contract and exclusion rules

An observation is one scalar absolute voltage maximum and its occurrence time.
Its unique key is `(source_file, simulation, terminal, phase)`. Source paths
preserve the distinction between equal run identifiers in different files.
For each source, expected keys are the Cartesian product of runs 1 through
NENERG and the declared terminals/phases. Equality with the observed key set,
plus rejection of duplicate keys, proves completeness before cleaning.
NENERG comes from the LIS declaration, not the observed row count; the existing
parser additionally rejects noncontiguous runs and declared/extracted mismatch.

The admissible occurrence interval is inclusive **[0, 0.3] seconds** for these
cases. The LIS miscellaneous-card echo supplies start/end time; every Tmax is
also checked against the paired ATP input. The ATP card has a blank start field
and declares a 10 microsecond step. ATPDraw defines Tmax as the simulation end
time in seconds: [official simulation settings](https://www.atpdraw.net/help7/html_simulations_settings.html).
This interval is a source-consistency bound, not a physically inferred transient
window. No lower bound based on random switch times is imposed, and the study
does not use table-dump time as the simulation end. No tolerance is needed for
the printed 0.3 s endpoint in these cases; endpoints are explicitly tested.

Non-finite voltage/time or out-of-window time excludes the affected measurement
with its original row index, identity and reason. Duplicate keys, missing keys,
unexpected selected keys, schema or identity errors block the dataset. A
partially cleaned table from a blocked dataset is not authorized for analysis.
Finite amplitudes are retained, including extremes; there is no sigma or
clustering cutoff in this cleaning stage. An empty cleaned selection blocks
analysis. Completeness is checked before exclusion: a missing raw observation
is a structural failure; an explicitly recorded measurement exclusion is a
traceable reduction of the analyzed sample.

## Evidence and actual results

The audit reuses the independent source transcriptions from the
[observation report](observation_structure_validation_report.md). It verifies
all LIS hashes, all key combinations, all occurrence times and all 60 recorded
voltage/time pairs. Numerical checkpoints cover phase A at first/last runs;
independence refers to transcription versus production extraction, not to an
independent reviewer or exhaustive numerical validation of phases B/C.

| Scenario | Files | Declared runs | Raw rows | Retained rows | Excluded |
| --- | ---: | ---: | ---: | ---: | ---: |
| SRPI | 5 | 11,350 | 102,150 | 102,150 | 0 |
| CRPI | 5 | 11,350 | 102,150 | 102,150 | 0 |
| Total | 10 | 22,700 | 204,300 | 204,300 | 0 |

Raw and cleaned tables are exactly equal for every real source. Consequently
cleaning changes neither the empirical sample nor any statistic computed on
that same sample. Observed times range from 0.01870 to 0.09997 s across the
files. No duplicate, missing combination, non-finite value or invalid time was
found. [Case ledger](evidence/cleaning_cases.csv) provides source hashes,
per-file counts and observed time ranges;
[execution log](evidence/cleaning_validation_2026-09-11.txt) records checks.

Controlled corruptions of the 100-run CRPI table have predetermined outcomes:

| Corruption | Input rows | Cleaned rows | Decision |
| --- | ---: | ---: | --- |
| Append a duplicate | 901 | 900 | Block analysis |
| Remove one observation | 899 | 899 | Block analysis |
| Set one time to 0.30001 s | 900 | 899 | Exclude one, retain remainder |
| Set one voltage to NaN | 900 | 899 | Exclude one, retain remainder |

The [corruption ledger](evidence/cleaning_corruptions.csv) retains altered
measurement values and issue context. A matrix-level missing-record issue has
no source row to retain; the deterministic script identifies the removed row
as the first original observation. Each one-row measurement exclusion reduces
the full table by 1/900 (0.1111%) and its affected terminal/phase group by
1/100 (1%). These artificial exclusions are not mixed into the accepted data.

Hand-specified adversarial tests additionally cover negative time, null/NaN
time, both endpoints, wrong run/source, missing cross-combinations despite
global phase/terminal presence, and retention of a finite 99 P.U. value.
The reporting regression verifies that metadata retains an excluded value and
its source identity. Successful pipeline exports retain all raw observations
and structured validation issues in `metadata.json`. Fatal validation raises
before statistical analysis/export; source inputs remain unchanged and the
audit ledger records the deliberately blocked experiments.

## Reproduction and thesis integration

Run from the repository root with local input files and the existing uv.lock:

```bash
rtk proxy sha256sum -c doc/evidence/cleaning_validation.sha256
rtk proxy uv run python -m scripts.audit_data_cleaning
rtk proxy uv run task format
rtk proxy uv run task lint
rtk proxy uv run task typecheck
rtk proxy uv run task test
```

The source paths and LIS/ATP hashes are in the case ledger. Reference line
numbers are in `parser_audit_checkpoints.csv` and `parser_crpi_checkpoints.csv`.
Implementation: `src/services/validation.py`, mandatory invocation in
`src/services/pipeline.py`, retained issue records in `src/services/reporting.py`.
Procedure: `scripts/audit_data_cleaning.py`. Test execution is recorded in
[evidence/cleaning_tests_2026-09-11.txt](evidence/cleaning_tests_2026-09-11.txt).
Ruff formatting/lint and BasedPyright passed; all 112 tests passed.
The thesis compiled successfully (41 PDF pages), with this subsection on
printed page 36. Compilation is only a technical check.
Thesis: `doc/main.tex`, subsection `Data integrity and cleaning validation`,
label `sec:data-cleaning-validation`.

## Limitations and reopening criteria

Acceptance concerns only the declared ten-file matrix, not the full project
scenario matrix under TCCKL-20/21. Direct callers that omit expected runs or
time bounds receive only the supplied checks. Simplified LIS fixtures lacking
a miscellaneous-card echo have no temporal bounds; that fallback is outside
this scientific acceptance. New layouts, restart conventions, time windows,
source revisions or observation definitions require renewed validation.

Zero observed exclusions is not proof of zero numerical simulation errors.
No waveform, timestep-convergence, missingness-mechanism, Gaussian adequacy or
physical-cause assessment is performed. In future data, even correctly recorded
exclusions can bias inference and require sensitivity analysis. The 60
purposive checkpoints do not support a probabilistic error-rate estimate.
Downstream historical artifacts are not regenerated or accepted by this audit.

The decision is justified by source-grounded expectations, exhaustive key and
time checks within scope, unchanged real samples, independently transcribed
numerical references, predicted corruption outcomes and traceable records.
It is not based on software tests or thesis compilation alone.
