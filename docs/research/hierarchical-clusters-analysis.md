# Hierarchical cluster image analysis

Analysis date: 2026-10-05.

This document records the initial analysis and implementation. For the
verified regenerated outputs and parameter sensitivity, see
[regenerated results analysis](hierarchical-regenerated-results-analysis.md).

## Evidence and method

Visually inspected all five `hierarchical_clusters.png` files under
`input_files/casos/*-simulacoes/resultados/`. Quantitative values below come
from the adjacent `annotated_observations.csv` files, not pixel estimates.
Each terminal contributes N observations in its corresponding case.

`src/services/clustering.py:cluster_hierarchical()` fits complete-linkage
clustering independently within each terminal, using only `value_pu`.
The pipeline uses the default maximum of two clusters. Labels are ordered
by mean voltage: zero is the lower-voltage group, one the higher group.
Position is a plotting coordinate, not a clustering feature. Horizontal
jitter is visual only. Labels do not identify anomaly or numerical error.

## Spatial pattern

All cases show the same ordering of observed maxima: `1_2LT` (line midpoint)
above `T_OPO` (opposite terminal), above `T_MAN` (switching terminal).
The larger datasets make the voltage bands denser, but point overlap hides
their internal density. These images alone do not establish Gaussianity,
distinct physical regimes, convergence, or the cause of extreme values.

| Simulations | T_MAN maximum | 1_2LT maximum | T_OPO maximum |
| ---: | ---: | ---: | ---: |
| 50 | 1.6517 | 2.0397 | 1.8792 |
| 100 | 1.5912 | 2.0496 | 1.8566 |
| 200 | 1.6621 | 2.1555 | 1.8736 |
| 1,000 | 1.6650 | 2.2361 | 1.8881 |
| 10,000 | 1.6760 | 2.2764 | 1.8919 |

Voltages are P.U. No observed maximum in these files exceeds 2.3 P.U.;
this is an empirical result, not proof of zero exceedance probability.
Comparing sample sizes does not establish that cases are nested samples.

## Partition stability

Each cell gives the highest value in cluster zero, lowest value in cluster
one, and percentage assigned to cluster one. The gap is the observed
separation between adjacent groups, not a calibrated physical threshold.

| Simulations | T_MAN: gap; high % | 1_2LT: gap; high % | T_OPO: gap; high % |
| ---: | --- | --- | --- |
| 50 | 1.3961–1.4336; 14.0% | 1.6402–1.6752; 50.0% | 1.5906–1.6319; 78.0% |
| 100 | 1.3865–1.3973; 26.0% | 1.4447–1.4656; 82.0% | 1.4631–1.5043; 94.0% |
| 200 | 1.3324–1.3465; 25.5% | 1.7274–1.7443; 47.0% | 1.3953–1.4329; 93.0% |
| 1,000 | 1.4151–1.4169; 12.4% | 1.6190–1.6241; 53.7% | 1.4651–1.4718; 90.9% |
| 10,000 | 1.3010–1.3011; 34.1% | 1.7010–1.7014; 46.8% | 1.4345–1.4358; 93.5% |

The spatial voltage ordering is consistent, but cluster boundaries vary
substantially. The 100-simulation midpoint assigns 82% to the upper group,
versus approximately 47–54% in the other cases. At T_MAN, upper membership
varies from 12.4% to 34.1%. At T_OPO the upper group is usually dominant.
Consequently, treating all green points as outliers would classify large
fractions of ordinary observations as suspect. The same color across
terminals represents local voltage rank, not a shared global voltage band.

## Presentation findings and next checks

- The images incorrectly display “K-Means Clusters” and “K-Means cluster”.
  `src/services/pipeline.py` reuses
  `src/services/visualization.py:plot_kmeans_clusters()` for hierarchical
  labels; that renderer hardcodes the K-Means title and legend.
- Vertical axis limits differ between images, weakening visual comparison.
- Only three terminal positions are observed; the scatter does not describe
  a continuous voltage profile along the line.
- Use shared axes, terminal names, sample counts, and method-correct labels.
- Add per-terminal distributions or density summaries to expose overlapping
  points, then quantify partition stability through repeated subsampling.
- Review terminal-phase grouping when multiple phases are included: the
  current hierarchical fit groups by terminal only.
- Validate extreme observations using waveform and simulation evidence
  before interpreting them as numerical errors or physical events.

No source code or result artifacts were changed during this analysis.

## Clarified target: separated upper groups

The requested behavior is to retain a nearby reference group and identify
a higher-voltage group separated from it, using ATP simulation extrema.
The annotated 50-simulation image highlights one T_MAN observation near
1.65 P.U., three midpoint observations near 2.01–2.04 P.U., and a dense
upper T_OPO band approximately around 1.73–1.88 P.U.

In the CSV, T_MAN has an adjacent gap of 0.1330 P.U. between 1.5187 and
1.6517; the midpoint has a gap of 0.0787 P.U. between 1.9303 and 2.0089,
leaving three observations above it. These support the first two marked
groups as locally separated upper tails. The largest T_OPO gaps are in
its lower tail; its marked upper band is densely populated and cannot be
equated with a rare high outlier group under the same rule.

Fixed complete-linkage `maxclust=2` does not enforce minimum separation,
upper-tail rarity, or a reference-density criterion. A revised method
needs an explicit separation criterion and may legitimately return no
separated upper group. The opposite-terminal annotation requires deciding
whether the objective is an upper operating regime or rare upper events.
These are different classification targets; matching circles alone would
not establish a defensible common statistical rule.

## Implemented upper-tail separation

Following the clarification that the third marked group is not required,
`cluster_hierarchical()` now uses sorted adjacent gaps, equivalent to
single-linkage merge distances in one-dimensional voltage data. It selects
the largest qualifying upper-tail gap per terminal, subject to:

- `min_gap_pu=0.05`: gap must exceed this absolute P.U. spacing.
- `gap_factor=5.0`: gap must exceed five times the median adjacent spacing,
  including zero gaps from repeated values.
- `max_tail_fraction=0.1`: selected upper tail contains at most 10% of rows.
- At least three reference observations remain below the cut.

No qualifying cut produces all-zero labels. Label one denotes a separated
upper tail, not a confirmed numerical error. These defaults are exploratory
choices for the requested behavior, not validated physical thresholds or
proof of statistical superiority. The absolute gap floor may suppress
selection as larger samples fill gaps; calibrate parameters before making
cross-sample conclusions. The previous `n_clusters` parameter is replaced
by the three separation parameters.

Patito models `HierarchicalObservation` and
`HierarchicalClusterObservation` in `src/services/schemas.py` validate the
required input projection and binary Int32 output labels. Additional
columns, custom column names, and original row order are preserved.
The shared scatter renderer now labels hierarchical results correctly.
The existing `hierarchical_tree.png` renderer remains a global Ward tree;
it is not a diagnostic tree for this terminal-local single-linkage rule.

Default-parameter checks on the five existing datasets produced:

| Simulations | T_MAN upper count | 1_2LT upper count | T_OPO upper count |
| ---: | ---: | ---: | ---: |
| 50 | 1 | 3 | 0 |
| 100 | 0 | 0 | 0 |
| 200 | 3 | 0 | 0 |
| 1,000 | 0 | 1 | 0 |
| 10,000 | 0 | 1 | 0 |

The 50-simulation preview is `doc/hierarchical-clusters-50-preview.png`.
Existing case CSV and PNG outputs were not regenerated by this change;
rerunning the pipeline applies the revised labels to those artifacts.
