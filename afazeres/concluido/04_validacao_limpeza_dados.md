# Data validation and cleaning

## Status

**Concluído — 2026-09-11.** Accepted for measurement integrity in the ten
complete-model, no-defect SRPI/CRPI files at 50/100/200/1,000/10,000 runs,
terminals T_MAN, 1_2LT and T_OPO, phases A/B/C, using 112677 V.

## Required evidence before Concluído

- [x] Define and verify source-run-terminal-phase uniqueness, declared versus
  extracted counts and completeness: all 204,300 keys match the declared
  matrix; no duplicates or missing observations.
- [x] Document admissible time ranges and exclusion rationale, retaining
  excluded records: source-declared [0, 0.3] s; finite extremes retained;
  zero real exclusions; altered values/reasons retained in the corruption
  ledger and successful pipeline metadata.
- [x] Validate deliberately corrupted and independently checked cases and
  sample effects: 60 source checkpoints matched; four controlled real-table
  corruptions produced expected decisions; hand-specified adversarial tests
  cover boundary, identity and cross-combination cases. Real sample unchanged.
- [x] Record date, reviewer, evidence, thesis location, limitations and decision:
  [validation report](../../doc/data_cleaning_validation_report.md).

## Evidence and acceptance decision

Reviewer: Codex (automated comparison; no independent human/electrical review).
The explicit scope, source-grounded expectations, complete key/time checks,
independent transcriptions and controlled failures justify acceptance for this
supporting data-cleaning task. Passing software tests alone is insufficient.

- [Per-file source hashes, counts and time ranges](../../doc/evidence/cleaning_cases.csv).
- [Retained corruption ledger](../../doc/evidence/cleaning_corruptions.csv).
- [Reproducible audit execution](../../doc/evidence/cleaning_validation_2026-09-11.txt).
- [Test execution](../../doc/evidence/cleaning_tests_2026-09-11.txt).
- [Evaluated code and evidence manifest](../../doc/evidence/cleaning_validation.sha256).
- [Thesis](../../doc/main.tex): `sec:data-cleaning-validation`,
  subsection `Data integrity and cleaning validation`.

Implementation: `src/services/validation.py`, `src/services/pipeline.py`,
`src/services/reporting.py`; procedure: `scripts/audit_data_cleaning.py`.
The previous 2026-09-07 review correctly identified absent integrity checks;
the implementation and audit above supersede that incomplete evidence.

## Limitations and related work

This is not physical anomaly validation or a complete experimental protocol.
TCCKL-20/21 retain responsibility for broader protocols/scenarios; TCCKL-23
retains physical-versus-numerical interpretation. Numerical checkpoints cover
phase A at first/last runs. Missing miscellaneous-card echoes are outside the
accepted temporal scope. Existing downstream artifacts require separate
regeneration/validation. Reopen if source bytes, layouts, keys or time windows
change or the accepted scope expands.
