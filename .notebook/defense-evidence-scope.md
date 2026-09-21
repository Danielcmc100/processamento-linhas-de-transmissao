# Defense Evidence Scope
> Final defense requires one evidence chain across code, data, manuscript, and review

Feature specification:
`specs/features/thesis-defense-evidence/spec.md`

Scientific plan:
`doc/defense_validation_plan.md`

Current manuscript gap:
`doc/main.tex` (L1081-1091)
- Applied statistics, probability, clustering parameters, and evaluation remain
  unfinished.

Current code risks:
- `src/services/comparison.py:compare_anomaly_methods()` treats the highest
  K-Means cluster as anomaly evidence.
- `src/services/pipeline.py:run_pipeline()` uses configured DBSCAN parameters
  without an adequacy or calibration gate.
- `src/services/statistics.py:summarize_statistics()` reports Gaussian tails
  without distribution-adequacy or confidence-interval evidence.

Data comparability risk:
- Saved configurations under `input_files/casos/` currently contain mixed
  100000 V and 112677 V bases; final comparable packages require regeneration.

Working-tree note:
- `specs/features/clustering-anomaly-correction/` was previously untracked and
  disappeared during feature reconnaissance. It was not restored. Required
  clustering correction is specified directly by DEF-08 through DEF-11.

Updated: 2026-09-20
