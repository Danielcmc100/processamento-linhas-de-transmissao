# Clustering Anomaly Diagnosis

Analysis date: 2026-09-20

## Finding

Current anomaly comparison incorrectly treats every observation in the
highest-centroid K-Means cluster as anomaly evidence. Across the available
50, 100, 200, 1,000, and 10,000 simulation datasets, this flags between
52.7% and 54.0% of analyzed rows.

K-Means receives only global `value_pu` values. Its labels primarily separate
normal voltage ranges and terminal positions. At 10,000 simulations, highest
cluster membership is 3.56% at `T_MAN`, 69.42% at `1_2LT`, and 88.31% at
`T_OPO`.

DBSCAN does not provide useful counter-evidence under current configurations.
Every target configuration uses `eps=3.0` and `min_samples=2` on unscaled P.U.
values, resulting in zero noise observations for all five datasets. A fixed
smaller `eps` is not sufficient because density changes with sample size.

## Required correction

- Preserve K-Means labels as descriptive clusters.
- Replace highest-cluster inference with explicit distance-to-centroid scores
  and calibrated thresholds.
- Fit and evaluate clustering within terminal-phase groups.
- Make DBSCAN scaling, calibration, applicability, and diagnostics explicit.
- Compare Boolean anomaly evidence rather than ordinal cluster labels.
- Preserve candidate terminology until physical or numerical causes receive
  domain validation.

Full requirements:
`specs/features/clustering-anomaly-correction/spec.md`.
