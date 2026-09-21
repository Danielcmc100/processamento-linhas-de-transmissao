# Thesis Defense Evidence Package Context

**Gathered:** 2026-09-20
**Spec:** `specs/features/thesis-defense-evidence/spec.md`
**Status:** Ready for design

## Feature boundary

Deliver one reproducible evidence chain from the ten declared SRPI/CRPI ATP
datasets through statistical and anomaly analyses, publication artifacts, and
the thesis manuscript. The feature stops before automatic insulation decisions
or unsupported physical-versus-numerical causal classification.

## Implementation decisions

### Statistical policy

- Empirical exceedance is primary and uses the strict `value_pu > threshold`
  event definition.
- Binomial uncertainty uses a two-sided 95% Wilson interval.
- Gaussian adequacy uses an Anderson-Darling test at 5%, supplemented by Q-Q,
  skewness, excess kurtosis, and empirical-versus-Gaussian tail differences.
- Rejected, inconclusive, undersized, or degenerate fits remain descriptive;
  they cannot replace empirical evidence.
- Robust screening uses a median/MAD score with an absolute threshold of 3.5.

### Anomaly policy

- Comparable groups are scenario, source lineage, terminal, and phase.
- K-Means labels are descriptive. Candidate evidence comes only from distance
  to the assigned centroid above a threshold fitted on development data.
- DBSCAN uses standardized features and a development-only nearest-neighbor
  calibration. Degenerate and all-noise fits are non-applicable.
- Method comparison consumes explicit Boolean flags and applicability states;
  ordinal cluster labels never count as evidence.
- Candidate-set stability uses identity-based Jaccard overlap. Values below
  0.80 are reported as sensitive, not failed or inaccurate.

### Controlled evidence and review

- Controlled data include clean controls plus point, contextual, and
  collective interventions at 1%, 5%, and 10% contamination.
- Splits use source lineage and simulation identity. Calibration sees only the
  development split.
- Review sampling covers agreement, disagreement, high score, threshold
  boundary, and non-flagged controls.
- Missing waveform, repeat-simulation, or qualified reviewer evidence forces
  the conclusion `unresolved`.

### Publication and reproducibility

- Final artifacts live under `results/defense-evidence/v1` with schema version
  `1.0.0` and immutable input/output hashes.
- Machine-readable CSV/JSON sources precede tables and figures.
- Publication figures use Okabe-Ito colors, distinct markers and line styles,
  SVG where supported, and 300 DPI PNG fallbacks.
- Generated LaTeX tables are included with `\\input`; displayed rounding does
  not alter source precision.
- All authored manuscript prose and generated manuscript labels use Brazilian
  Portuguese.

## Agent discretion

- Internal module boundaries, typed record representation, and exact file
  names may change if requirement traceability remains intact.
- Test fixtures may use smaller deterministic samples than production runs.
- Final package status remains incomplete when required source, review, or
  quality evidence is unavailable.

## Specific references

- Scientific protocol: `doc/defense_validation_plan.md`.
- Existing manual review protocol:
  `doc/manual_anomaly_detection_and_test_design.md`.
- Accepted parser, observation, P.U., and cleaning evidence: `doc/evidence/`.

## Deferred ideas

- Automated insulation-level recommendation.
- Company expert-system logic.
- Automatic causal labeling of ATP numerical errors.
- Oral-defense slide deck.
- Repeat ATP simulation when the external ATP runtime is unavailable.
