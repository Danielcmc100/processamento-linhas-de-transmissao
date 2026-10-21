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

## How the current hierarchical rule works

For each terminal, the rule sorts the P.U. voltages and computes each gap
between adjacent values. In one dimension these gaps represent the
single-linkage merge distances. It considers only cuts leaving at least
three reference observations and an upper tail no larger than
`max_tail_fraction` of that terminal's observations. A candidate gap must
be strictly greater than both `min_gap_pu` and `gap_factor` times the median
adjacent gap. Among eligible gaps, the largest defines the cut. Values
above it receive label 1; the rest receive label 0. If no gap qualifies,
all labels are 0. Fewer than four observations also yield all zeros.

For example, consider ten sorted voltages from 1.00 to 1.08 P.U. in steps
of 0.01, followed by 1.20 P.U. Their median gap is 0.01 P.U. With the
documented defaults, the required gap is greater than 0.05 P.U. The final
gap is 0.12 P.U. and leaves one of ten observations in the upper tail,
so only 1.20 P.U. receives label 1.

This rule does not accept a requested number of clusters. Its two labels
mean reference and separated upper tail; they do not prove that a voltage
is a numerical error or a physical event. K-Means uses an explicit `k`
and partitions comparable scenario, source, terminal, and phase groups.
The Ward dendrogram plots a different, global hierarchy and does not
explain the terminal-local upper-tail labels.
