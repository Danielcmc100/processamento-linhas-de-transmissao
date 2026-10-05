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

Hierarchical clustering: `src/services/clustering.py:cluster_hierarchical()`
- Uses terminal-local sorted gaps, equivalent to 1D single-linkage distances
- Selects upper tails of at most 10% beyond gaps exceeding both 0.05 P.U.
  and five times median adjacent spacing; requires three reference rows
- Returns zero throughout when no gap qualifies; label one is descriptive
- Patito input/output projections validate required values and binary labels
- Fifty-simulation regression selects one T_MAN and three 1_2LT rows,
  with no T_OPO selection
- Parameters are exploratory; larger samples may fill gaps
- Global Ward dendrogram remains separate from this terminal-local rule
- Details: `doc/hierarchical-clusters-analysis.md`

Correction spec:
`specs/features/clustering-anomaly-correction/spec.md`

Updated: 2026-10-01
