# Regenerated hierarchical clustering results

Analysis date: 2026-10-05.

## Evidence

Inspected `hierarchical_clusters.png` in all five case result directories
and measured values from the adjacent `annotated_observations.csv` files.
Recomputed labels using the current `cluster_hierarchical()` defaults:
all stored labels match, row for row, in every dataset. This verifies label
consistency with the implementation, not physical validity.

Each dataset has N analyzed phase-A observations per terminal (3N total).
Counts below are observations, not necessarily distinct simulation runs:
simulation 41 in the 50-shot case is selected at two terminals.

## Selected upper groups

| Shots | Terminal | Selected / terminal N | Selected P.U. range | Reference maximum | Separating gap |
| ---: | --- | ---: | --- | ---: | ---: |
| 50 | T_MAN | 1/50 (2%) | 1.651738 | 1.518730 | 0.133009 |
| 50 | 1_2LT | 3/50 (6%) | 2.008931–2.039735 | 1.930255 | 0.078676 |
| 100 | All terminals | 0/100 each | None | — | — |
| 200 | T_MAN | 3/200 (1.5%) | 1.635841–1.662103 | 1.584116 | 0.051725 |
| 1,000 | 1_2LT | 1/1,000 (0.1%) | 2.236110 | 2.153653 | 0.082457 |
| 10,000 | 1_2LT | 1/10,000 (0.01%) | 2.276433 | 2.209240 | 0.067193 |

Every unlisted terminal has no selected upper observations. T_OPO has no
selected group in any dataset, matching the clarified target.

Selected simulation IDs:

- 50 shots: T_MAN 41; 1_2LT 13, 20, and 41.
- 200 shots: T_MAN 45, 79, and 188.
- 1,000 shots: 1_2LT 816.
- 10,000 shots: 1_2LT 1072.

## Interpretation by sample size

The 50-shot result reproduces both requested marked groups. Most midpoint
observations around 1.7–1.9 P.U. now remain in the reference group, rather
than being selected merely because their voltages are relatively high.

The 100-shot result has no qualifying separation. Largest eligible upper
gaps are 0.045387 P.U. at T_MAN, 0.031007 at 1_2LT, and 0.012269 at T_OPO:
all lie below the 0.05 P.U. floor. All-blue rendering is therefore expected;
it does not mean all simulations are physically validated.

The 200-shot result selects three upper T_MAN observations, but its
0.051725 P.U. gap is only 0.001725 P.U. above the floor. This classification
is sensitive to the configured threshold. The midpoint reaches 2.155531
P.U. without selection because its largest eligible upper gap is 0.044844
P.U. High absolute voltage alone does not trigger this method.

At 1,000 and 10,000 shots, the midpoint maximum remains locally isolated
despite a much denser reference distribution. One observation is selected
in each dataset. The two selected runs are not established to be the same
underlying event, and the datasets are not established to be nested.

## Parameter sensitivity

Recomputed labels with a small parameter sweep, without changing artifacts:

- Lowering `min_gap_pu` from 0.05 to 0.04 adds two T_MAN observations in
  the 100-shot dataset and eleven midpoint observations in the 200-shot
  dataset. Other case counts remain unchanged.
- Raising `min_gap_pu` to 0.06 removes the three T_MAN selections at 200
  shots. Other case counts remain unchanged.
- Raising `gap_factor` from 5.0 to 5.5 removes the three midpoint selections
  at 50 shots. The baseline effective threshold there is 0.072601 P.U.,
  versus a 0.078676 P.U. observed gap; at factor 5.5 it becomes approximately
  0.079861 P.U. Other case counts remain unchanged.

The isolated midpoint selections at 1,000 and 10,000 shots survive all
these tested settings. This is limited local parameter robustness, not
bootstrap stability or evidence that they are numerical errors.

## Limits and conclusion

The regenerated scatter plots satisfy the requested behavior: highlight
small, separated upper groups and permit no selected group. They no longer
force two voltage partitions per terminal. The higher sample sizes still
show the largest observed voltages at the midpoint, and no maximum in these
datasets exceeds 2.3 P.U.

The 0.05 P.U. absolute floor controls every terminal/case combination
except the 50-shot midpoint. Consequently, apparent cross-sample changes
depend strongly on whether observations fill a voltage gap. Decreasing
selected fractions alone does not prove convergence or reduced error rate.
Reference label zero means no separated upper tail was selected, not
confirmed normal behavior. Label one does not imply physical or numerical
cause, and it remains separate from the pipeline's anomaly consensus:
the three selected midpoint observations at 50 shots have
`anomaly_candidate=false` in the CSV.

The title and legend now correctly identify hierarchical clustering.
Vertical axes still differ, and point overlap hides density in larger
datasets. The separate `hierarchical_tree.png` uses global Ward linkage,
so it cannot justify the terminal-local single-linkage selections.

For academic validation, report the separation gap, effective threshold,
selected count, and parameter sensitivity per terminal. Further checks
should measure resampling stability and compare selected runs with ATP
waveform/simulation evidence. No clustering or result files were modified
for this analysis.
