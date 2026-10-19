# Prerequisites for a Defensible Overvoltage Probability Experiment

## Core decision

The article case and the engineering case must be treated as separate
experiments.

- The article case is a benchmark for parser, GTPPLOT, and statistical
  reproduction.
- The project case estimates probability for the actual transmission system.

Changing the physical project model until its histogram resembles the article
would change the target population. The resulting probability would no longer
describe the original project case.

## Required event definition

Freeze the event before running simulations:

- electrical scenario and topology;
- terminal and voltage type: phase-ground or phase-phase;
- one phase or maximum across phases;
- peak-search time window;
- strict comparison operator, such as `value_pu > threshold_pu`;
- physical voltage base and threshold in both volts and p.u.;
- treatment of invalid ATP runs and numerical anomalies.

The event definition must be stored with each result. Probabilities from
different event definitions are not directly comparable.

## Required stochastic model

Input distributions must represent breaker data or an explicit engineering
assumption:

- common closing-angle distribution;
- pole-specific closing-time mean and standard deviation;
- dependence or correlation between poles;
- truncation and physical bounds;
- separate scenarios for faults, trapped charge, or pole disagreement.

The article's switching standard deviation must not be copied only to widen
the project histogram. Doing so defines a different breaker population.

## Required numerical controls

Lock and document:

- ATP version and input hash;
- line and terminal models;
- source frequency;
- simulation time step and end time;
- initialization conditions;
- random seed or random-number provenance;
- number of requested and successfully parsed energizations.

Run time-step and simulation-window sensitivity checks. The probability is
credible only if relevant peaks and exceedance counts remain stable under a
reasonable numerical refinement.

## Required data lineage checks

Before estimating probability:

- keep node and branch quantities distinct;
- keep phase-ground and phase-phase bases distinct;
- prohibit duplicate terminal-phase identities;
- reconcile parsed observations with ATP frequency tables;
- confirm one valid observation per event unit and energization;
- record exclusions with explicit reasons.

`coisas/results/artigo-1000` fails these conditions because it represents
100 runs and mixes a phase-phase branch magnitude with phase-A node data. It
must not be used as article phase-ground evidence.

## Probability estimator

Use direct exceedance as the primary estimator:

`estimated_probability = exceedance_count / valid_simulation_count`

Report a binomial confidence interval with it. Histogram bin width affects
visual appearance, but it must not affect the direct event count.

Use a fitted Gaussian only as a secondary model after distributional
adequacy is supported. Current project samples reject normality, so Gaussian
tail probabilities are descriptive extrapolations, not primary evidence.

## Sample-size interpretation

For zero observed exceedances, the upper endpoint of a two-sided 95% Wilson
interval is approximately `z^2 / (n + z^2)`. Required zero-event sample sizes
for selected upper limits are:

| Desired 95% upper limit | Minimum simulations |
|---:|---:|
| 0.10% | 3,838 |
| 0.05% | 7,680 |
| 0.01% | 38,411 |

Existing zero-event interpretations are:

| Simulations | Observed exceedances | Wilson 95% upper limit |
|---:|---:|---:|
| 50 | 0 | 7.1348% |
| 1,000 | 0 | 0.3827% |
| 10,000 | 0 | 0.0384% |

Therefore, 10,000 zero-event runs support an upper bound near 0.0384%, not a
claim of zero probability.

## Convergence requirement

Use independent, reproducible batches. For each cumulative batch, track:

- direct exceedance probability and Wilson interval;
- upper quantiles near the engineering threshold;
- maximum value as a diagnostic only;
- invalid-run and anomaly rates;
- stability by terminal and phase.

Stop only after a predeclared precision target is met. Similar-looking
histograms are not a stopping criterion.

## Article reproduction benchmark

To reproduce the article distribution, match its experiment rather than only
its plot style:

- 100 km simple JMarti line;
- 50 Hz sources;
- 20 microsecond time step and 50 millisecond end time;
- 100 kV phase-ground base;
- switching mean 20 milliseconds and standard deviation 1 millisecond;
- common 0--360 degree delay with `STATFR = 60 Hz`;
- the same node, branch, and maximum-of-phases variables;
- 1,000 energizations and 0.05 p.u. GTPPLOT compartments.

This benchmark validates reproduction. It must remain isolated from the SRPI
probability estimate.

## Recommended project artifacts

Maintain two explicit configurations:

1. `benchmark_article_original`: exact method-reproduction benchmark.
2. `srpi_probability_v1`: frozen engineering estimand and physical model.

The second configuration should declare its threshold, target confidence
interval width, minimum sample size, seed strategy, and numerical convergence
tests before production runs.

## Method references

- SciPy `BinomTestResult.proportion_ci` documents exact, Wilson, and
  continuity-corrected Wilson intervals.
- NIST Engineering Statistics Handbook describes Wilson score intervals for
  binomial proportions.
- SciPy quasi-Monte Carlo guidance documents space-filling designs and warns
  that their design rules must be preserved.

