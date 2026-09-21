# Clustering Anomaly Flow
> Global K-Means labels currently act as anomaly evidence

Entry: `src/services/pipeline.py:run_analysis()`
Flow: per-terminal DBSCAN → global K-Means → sigma flags → method comparison

K-Means: `src/services/clustering.py:cluster_kmeans()`
- Fits only `value_pu` globally after standardization
- Labels ordered by centroid; labels describe voltage partitions

Comparison: `src/services/comparison.py:compare_anomaly_methods()`
- Highest K-Means label currently counts as anomaly signal
- Target datasets therefore flag approximately 53% of rows

DBSCAN: `src/services/clustering.py:detect_outliers_dbscan_per_terminal()`
- Per-terminal fit uses raw P.U. values
- Current target configs use `eps=3.0`, `min_samples=2`; all rows label zero

Correction spec:
`specs/features/clustering-anomaly-correction/spec.md`

Updated: 2026-09-20
