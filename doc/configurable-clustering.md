# Configurable clustering

The analysis JSON configures K-Means through `kmeans.n_clusters` and
`kmeans.random_state`. The pipeline passes both values to grouped K-Means
evidence. The cluster count must be positive; groups with too few
calibration observations yield non-applicable K-Means evidence.

The same JSON configures hierarchical upper-tail separation through
`hierarchical.min_gap_pu`, `hierarchical.gap_factor`, and
`hierarchical.max_tail_fraction`. These values are passed directly to
`cluster_hierarchical()` for terminal-local labels. The minimum gap must
be positive, the factor at least one, and the upper-tail fraction strictly
between zero and 0.5. All three must be finite. If `hierarchical` is
omitted, the documented defaults (0.05 P.U., 5.0, and 0.1) apply.

The five maintained `input_files/casos/*-simulacoes/input.json` examples
specify both clustering sections. The saved `configuration.json` includes
effective values for reproducibility. The hierarchical cluster plot uses
these labels; the separate Ward dendrogram remains a visualization with
its own method.
