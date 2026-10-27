# Generated Case Plots Analysis

> Historical record: output-voltage three-sigma requirements and detector
> descriptions below were superseded on 2026-10-26 by READ-07 in
> `specs/features/thesis-readability-and-sigma-correction/spec.md`.
> Active candidates use applicable MAD, K-Means distance and DBSCAN noise.
> Preserve switching configuration and independent Gaussian diagnostics;
> historical results below remain evidence of their original execution.


## Scope

This analysis covers the SRPI result packages under `input_files/casos` for
50, 100, 200, 1,000, and 10,000 simulations. All packages select phase A,
terminals `T_MAN`, `1_2LT`, and `T_OPO`, base voltage 112,677 V, and strict
exceedance threshold 2.3 p.u.

## GTPPLOT-style histograms

The new histograms are numerically correct reproductions of the individual ATP
peak-voltage tables. Direct right-closed counts, using 0.05 p.u. compartments,
were compared with every phase-A source bin in each `case.lis`:

| Simulations | ATP bins checked | Mismatches |
|---:|---:|---:|
| 50 | 49 | 0 |
| 100 | 44 | 0 |
| 200 | 53 | 0 |
| 1,000 | 54 | 0 |
| 10,000 | 58 | 0 |

The plots therefore preserve ATP frequency semantics: one peak per
energization and compartment rule `lower < peak <= upper`.

### Stable distribution features

At 10,000 simulations:

| Terminal | Mean (p.u.) | Median | P95 | P99 | Modal compartment |
|---|---:|---:|---:|---:|---:|
| `T_MAN` | 1.2737 | 1.2467 | 1.5094 | 1.5865 | (1.15, 1.20] |
| `1_2LT` | 1.6570 | 1.6759 | 1.9781 | 2.0837 | (1.85, 1.90] |
| `T_OPO` | 1.7006 | 1.7477 | 1.8287 | 1.8498 | (1.75, 1.80] |

`1_2LT` has the widest distribution and the largest extreme values. `T_OPO`
has a strong concentration near 1.8 p.u. and a long lower tail. `T_MAN` is
right-skewed, with most peaks near 1.2 p.u. and a thinning upper tail.

The terminal modes are already visible at small sample sizes, except for
`T_MAN`, whose modal upper boundary changes from 1.25 p.u. at 50-200 samples to
1.20 p.u. at 1,000-10,000 samples. This is ordinary small-sample variability.

### Convergence

Using the 10,000-simulation histograms as references, total-variation distance
for 1,000 simulations is 0.0404 at `T_MAN`, 0.0673 at `1_2LT`, and 0.0430 at
`T_OPO`. Fifty simulations give 0.1656, 0.2824, and 0.1373 respectively.

Thus 50-200 runs are useful for exploratory shape inspection but remain noisy,
especially for the broad `1_2LT` distribution. The 1,000-run results reproduce
central shape reasonably well. The 10,000-run results provide the strongest
available empirical tail evidence.

## Exceedance plots

At 10,000 simulations, direct strict exceedance counts are:

| Terminal | `P(X > 1.8)` | `P(X > 2.0)` | `P(X > 2.3)` |
|---|---:|---:|---:|
| `T_MAN` | 0% | 0% | 0% |
| `1_2LT` | 32.71% | 3.73% | 0% |
| `T_OPO` | 16.94% | 0% | 0% |

Zero occurrences above 2.3 p.u. do not establish zero physical probability.
The two-sided 95% Wilson upper limit is 7.135% at 50 simulations, 0.3827% at
1,000 simulations, and 0.03840% at 10,000 simulations. Conclusions must remain
conditioned on the simulated SRPI experiment.

### Meaning of the Wilson upper limit

The empirical estimate is `k / n`. When `k = 0`, this estimate is zero, but a
finite experiment cannot exclude a small nonzero probability. A binomial
confidence interval quantifies that sampling uncertainty. For zero occurrences,
the upper endpoint of the two-sided 95% Wilson interval is

\[
p_{upper} = \frac{z^2}{n + z^2}, \qquad z = 1.96.
\]

For 10,000 simulations, this gives

\[
p_{upper} = \frac{1.96^2}{10000 + 1.96^2}
\approx 0.000384 = 0.0384\%.
\]

Interpretation: the experiment observed no exceedance, while probabilities up
to approximately 0.0384% remain compatible with the sample under this interval
procedure. This is not a 95% probability that the unknown parameter lies below
the endpoint. In repeated equivalent experiments, 95% Wilson intervals are
constructed to cover the true binomial probability approximately 95% of the
time.

Empirical curves visibly disagree with Gaussian curves, most clearly for
`T_OPO`, whose steep upper transition and long lower tail are not symmetric.
Anderson-Darling rejects normality at 5% for every terminal and every inspected
sample size. Gaussian overlays are therefore descriptive only; empirical
survival curves and binomial intervals must carry probability claims.

## Combined distribution plot

The combined scatter correctly shows terminal ordering and voltage spread:

- `T_MAN`: lowest central level and narrow upper range;
- `1_2LT`: widest range and only terminal reaching above 2.0 p.u.;
- `T_OPO`: highest concentration but bounded near 1.9 p.u.

Gaussian side profiles should not be read as validated density models because
adequacy tests reject normality. Dashed three-sigma markers have the same
limitation.

## Clustering plots

- K-Means creates two descriptive voltage partitions inside every terminal.
  These are not physical anomaly classes.
- DBSCAN assigns every observation to one cluster under `eps = 3.0` and
  `min_samples = 2`; its plot contains no noise evidence and adds little
  discrimination.
- Hierarchical terminal-local output selects only very small upper tails at
  large sample sizes. At 10,000 simulations, one visible `1_2LT` observation
  forms cluster 1. Such labels remain candidates, not confirmed ATP errors.
- The global Ward dendrogram is readable for 50 samples but its sample-index
  axis is unusable at 10,000 samples. It should not be used as a presentation
  figure at that scale without truncation or aggregation.

Current anomaly counts grow with sample size, particularly in the left tail of
`T_OPO`, because MAD responds to the pronounced negative skew. This is not
evidence that more simulations create more numerical errors; it shows that a
symmetric robust-distance rule still reacts to an asymmetric physical output
distribution.

## Presentation-quality findings

The GTPPLOT panels are legible and preserve independent terminal scales. One
formatting inconsistency remains: the overall figure title appears in the 50,
200, and 10,000 outputs but is absent from the 100 and 1,000 outputs. Regenerate
all result packages from one code revision before using figures in the thesis.

Recommended thesis evidence order:

1. GTPPLOT-style empirical histograms;
2. empirical exceedance curves and confidence intervals;
3. adequacy-test result rejecting Gaussian inference;
4. clustering plots labeled exploratory;
5. truncated or omitted dendrogram for large samples.
