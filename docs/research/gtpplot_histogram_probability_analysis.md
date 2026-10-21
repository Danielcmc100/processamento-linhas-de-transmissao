# GTPPLOT Histogram and Probability Analysis

## Scope

This note compares the method described in `2000-N4-Estati-1.pdf` with the
histograms generated from `input_files/casos`. It focuses on peak
phase-to-ground voltage observations and empirical exceedance probability.

## Method described by Hevia

The ATP statistical study produces one positive peak per energization and per
requested variable. A grouped request also produces one value per
energization, but that value is the maximum peak among variables in the group.
Therefore, every individual or grouped table has exactly `NENERG` observations.

Each ATP table reports:

- `Frequency (density)`: count in one compartment;
- `Cumulative frequency`: count accumulated through that compartment;
- `Per cent .GE. current value`: ATP-provided exceedance percentage.

With a positive `AINCR`, compartment width is fixed in p.u. The example uses
`AINCR = 0.05`. With negative `AINCR = -NCOMP`, ATP instead uses exactly
`NCOMP` compartments. `NSTATI` changes only horizontal-axis representation in
GTPPLOT: interval number, p.u., or physical units.

GTPPLOT also reports the Gaussian approximation

\[
X_{2\%} = \bar{X} + 2.0537494s.
\]

This is a model-based 2% exceedance level. It is not a direct empirical count.

## Why current figures differ

The source document and current project figure do not use the same graphical
contract.

1. The document shows a separate filled-bar histogram for each variable and a
   separate grouped `SUMMARY` histogram. Current code overlays three terminal
   histograms on one axis as unfilled step lines.
2. ATP uses the configured `AINCR = 0.05 p.u.`. Current code asks NumPy for 20
   equal bins over the combined minimum-to-maximum range of all terminals.
   Edges therefore change with sample and terminal range and are not guaranteed
   to fall on ATP's 0.05 p.u. boundaries.
3. The document example uses 1000 shots. A 50-shot histogram has only 50
   observations per terminal and is necessarily sparse. Its appearance cannot
   be expected to match the smoother example.
4. Histogram shape depends on the electrical network, switching-time
   distribution, monitored node, phase, and grouping policy. Matching binning
   and sample size makes presentation comparable, but does not imply matching
   distribution shape across different studies.
5. Current pipeline selects phase `A` from configuration before plotting. It
   does not reproduce the document's four panels for phases A, B, C, and the
   maximum-of-group `SUMMARY` observation.

Concrete project evidence: the 1000-shot SRPI `case.lis` declares
`AINCR = 0.050`. Its `T_MANA` table contains 14 compartments from 1.05 through
1.70 p.u.; frequencies sum to 1000. Its ungrouped mean and sample standard
deviation, 1.26673156 and 0.118402192 p.u., agree with project summaries.

## Probability definition

Define event first. For terminal `T`, phase `A`, and threshold `u`, one useful
event is

\[
E = \{\max_t |V_{T,A}(t)| / V_{base} > u\}.
\]

With `k` occurrences among `n` valid independent energizations, empirical
probability is

\[
\hat{p} = k/n.
\]

For an interval `(a, b]`, count observations satisfying that exact boundary
rule and divide by `n`. For ATP compartments, preserve ATP's printed
frequencies and thresholds instead of reconstructing different bins.

The ATP heading says `.GE.`, but its printed table is tied to compartment
boundaries. In the example, cumulative count 1 at 1.10 p.u. corresponds to
99.9%, or `(1000 - 1) / 1000`. Direct-observation comparisons must therefore
state whether `>` or `>=` is used and report observations exactly on the
threshold.

## Results already available

For configured event `value_pu > 2.3`, phase A, SRPI:

| Shots | Terminal | Occurrences | Empirical probability | 95% Wilson upper bound |
|---:|---|---:|---:|---:|
| 50 | all three | 0 | 0% | 7.135% |
| 1000 | all three | 0 | 0% | 0.3827% |
| 10000 | all three | 0 | 0% | 0.03840% |

Zero observed occurrences do not prove zero physical probability. They bound
the probability under the simulated experiment. This experiment-conditioned
interpretation must include scenario, switching assumptions, terminal, phase,
base voltage, event definition, exclusions, and effective sample count.

At lower thresholds, direct counts show expected variation. For 1000 shots:

- `1_2LT`, phase A: 338/1000 exceed 1.8 p.u.; 45/1000 exceed 2.0 p.u.;
- `T_OPO`, phase A: 175/1000 exceed 1.8 p.u.; none exceed 2.0 p.u.;
- `T_MAN`, phase A: none exceed 1.8 p.u.

## Gaussian limitation

Anderson-Darling results in every inspected 50, 100, 200, 1000, and 10000-shot
phase-A terminal group reject normality at 5%. Gaussian tail probabilities in
current outputs are therefore descriptive only. Direct empirical probability
and its binomial confidence interval should be primary evidence. A Gaussian
extrapolation must be visibly labeled as model-dependent, not substituted for
observed frequency.

## Recommended reproduction contract

To reproduce GTPPLOT presentation faithfully:

1. Read bins directly from each ATP statistical table in `case.lis` using
   `parse_statistical_distributions()`.
2. Plot one filled-bar panel per terminal-phase table, using ATP thresholds and
   `frequency_count`; show `NENERG` in the legend.
3. Plot grouped `SUMMARY` separately when maximum-across-variables behavior is
   required.
4. Plot exceedance as a descending step curve from ATP cumulative counts or as
   a direct empirical survival curve with explicit boundary semantics.
5. Keep current overlaid 20-bin plot only as a comparative visualization; do
   not label it a GTPPLOT reproduction.

## Implemented individual-table reproduction

`plot_gtpplot_histograms()` now generates a separate panel for each selected
terminal-phase group. It uses fixed 0.05 p.u. compartments, ATP's
`lower < value <= upper` boundary rule, outlined bars, and shot counts. The
pipeline writes this figure as `gtpplot_histograms.png` while preserving the
existing comparative histogram.

This plot reproduces individual ATP peak-voltage tables. It intentionally does
not claim to reproduce the grouped `SUMMARY` table, which requires one
maximum-across-variables observation per energization.

## Code pointers

- ATP table parser: `src/parser/statistical_distribution.py`
- Current histogram: `src/services/visualization.py:plot_overvoltage_histogram()`
- GTPPLOT-style individual panels:
  `src/services/visualization.py:plot_gtpplot_histograms()`
- Phase selection and plotting flow: `src/services/pipeline.py:run_pipeline()`
- Direct probability and Wilson interval:
  `src/services/statistical_evidence.py:summarize_statistical_evidence()`
- ATP/direct boundary reconciliation:
  `src/services/probability_reconciliation.py:reconcile_probability_bin()`
