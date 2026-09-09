# Project State

**Updated:** 2026-09-08

## Decisions

- The academic scope ends at validated data analysis; automated insulation
  optimization remains outside the TCC.
- Each configured run analyzes one explicit phase to avoid mixing phase
  distributions.
- DBSCAN noise is treated as a candidate anomaly, not definitive proof of a
  numerical ATP error.
- Existing code and project documentation are written in English where the
  repository conventions require it; the TCC manuscript remains in Portuguese.

## Blockers and risks

- Gaussian assumptions and DBSCAN parameters have not yet been validated on
  the target dataset.
- No normality test, goodness-of-fit test, or confidence interval is currently
  calculated.
- Statistical validation cannot distinguish physical events from numerical
  artifacts using clustering alone; domain evidence is required.

## Completed software capability

- A validated JSON configuration drives a machine-independent, single-phase
  pipeline through parsing, cleaning, DBSCAN, K-Means, sigma comparison,
  summaries, and plots.
- The artifact writer produces seven auditable outputs with deterministic
  tables/configuration, input hashes, counts, software versions, and an
  explicit overwrite policy.
- The implementation and quality-gate evidence are documented in
  `doc/validation-evidence.md`.
- Parser fidelity is accepted for the audited real ATP layouts. The evidence
  covers 235 primary files, 533,450 runs, and independently transcribed
  checkpoints in `doc/parser_validation_report.md`.

## Next actions

- Validate model assumptions and parameters, then review candidate anomalies
  with electrical-engineering domain evidence.
- Use the target-dataset artifacts in the TCC methodology and results
  chapters without extending the software into insulation optimization or an
  expert system.
