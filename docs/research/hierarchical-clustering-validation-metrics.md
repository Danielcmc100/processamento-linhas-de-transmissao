# Validation metrics for hierarchical upper-tail selection

Date: 2026-10-07.

## Scope

The current `cluster_hierarchical()` uses terminal-local, one-dimensional
voltage gaps. Its label 1 means a separated upper tail, not a verified ATP
numerical error. The three plotted line positions are not input features.
The separate `hierarchical_tree.png` uses global Ward linkage and does not
represent this selection rule.

For the 50-shot phase-A case, the stored results select 1/50 observations
at T_MAN, 3/50 at 1_2LT, and 0/50 at T_OPO. The corresponding selected gaps
are 0.133009 and 0.078676 P.U. These are descriptive results, not
validation scores.

## Recommended evidence, in priority order

1. **Reviewed-event precision and recall.** Have electrical-domain reviewers
   classify selected and sampled unselected runs as plausible physical
   extremes, suspected numerical artifacts, data defects, or unresolved.
   Calculate precision, recall, and false-positive rate separately for a
   precisely defined target. Do not treat unresolved events as ground truth.
   A small positive class also warrants reporting counts and uncertainty.
2. **Selection stability.** Refit within each terminal after repeated
   run-level subsampling and small parameter changes. For each retained
   observation, report how often it stays selected; report selected count
   and selected-set Jaccard overlap when both sets are nonempty. Record
   empty selections separately. Keep all observations from one simulation
   together. Do not compare unrelated simulation IDs across sample sizes.
3. **Gap strength and sensitivity.** Report selected count, largest selected
   gap in P.U., effective threshold
   `max(min_gap_pu, gap_factor * median_adjacent_gap)`, and their ratio.
   Repeat for plausible `min_gap_pu`, `gap_factor`, and `max_tail_fraction`
   values. Gap ratio quantifies margin to this rule's own cutoff; it does
   not independently prove that the split is physically meaningful.
4. **Controlled detection tests.** On held-out runs, compare methods using
   reviewed physical extremes and controlled perturbations with known
   provenance. Report recall by perturbation type and intensity, plus
   false-positive rate on valid runs. Injected values are not ATP errors.
   Compare methods under a shared event definition, grouping policy,
   feature space, and operating-point policy.

Silhouette, Davies-Bouldin, and Calinski-Harabasz can be secondary
descriptions when at least two clusters exist. They are undefined for an
all-zero selection, sensitive to singleton or highly imbalanced upper
groups, and optimize geometric separation rather than correct anomaly
screening. In this case, the gap rule selects on the same voltage used by
the indices, making a high internal score partly circular. Do not use one
of these indices alone to rank the methods.

Adjusted Rand Index compares two partitions on the same observations and
can support stability analysis. It cannot establish physical correctness
without reviewed labels. Selected-set Jaccard is easier to interpret for
the rare upper group, provided empty and singleton cases are reported.

## Sources

- scikit-learn clustering evaluation and metric definitions:
  https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation
- scikit-learn silhouette score conditions:
  https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- Hennig (2007), cluster-wise Jaccard stability:
  https://doi.org/10.1016/j.csda.2006.11.025
