# Thesis completion assessment: advisor conversation and ATP article

Assessment date: 2026-10-17.

## Decision and scope

The defensible contribution is reproducible extraction, empirical probability
analysis, and selection of ATP observations for further technical review.
Internal clustering quality does not establish numerical-error detection.
The advisor's message proposes an optional specialist assessment of whether
selected cases deserve investigation, not mandatory causal classification.
Academic acceptance of this scope remains the advisor's decision.

This assessment reads the supplied chat, all extracted article text, visual
checks of article pages 5 and 9, current manuscript sections, relevant source
functions, and saved evidence tables. It does not rerun ATP, statistical
experiments, software tests, or the manuscript build. Existing working-tree
changes were preserved. Counts below describe saved artifacts, not newly
validated experiments. The RTK command required by local instructions was
unavailable; ordinary local tools were used after the failed invocation.

## What the conversation actually requests

Source: [chat.txt](../chat.txt), exported timestamps 10/9/26 and 10/10/26.
The locale of the exported dates is not declared. Images were omitted from
the text export but subsequently supplied in the conversation. The visual
assessment below updates that limitation; raw inputs and fitting settings
remain unavailable for independent reproduction of the advisor's analysis.

| Advisor statement | Required response | Acceptance evidence |
| --- | --- | --- |
| Asymmetric histograms are poorly represented by a Gaussian | Keep empirical exceedance primary; compare gamma and lognormal | Reproducible fit comparison, diagnostics, and qualified conclusions |
| Evaluate group separation rather than accuracy | Calculate Silhouette and Davies-Bouldin on comparable partitions | Table with group identity, sample count, features, parameters, cluster sizes, metrics, and applicability |
| Exploratory tests favored different methods on different indices | Reproduce both named subsets before extending the study | CRPI, 50 runs, 1_2LT, phase A; SRPI, 50 runs, T_MAN, phase B |
| Perhaps ask a specialist whether selected cases deserve analysis | Obtain a traceable usefulness review if available | Case-level assessment, rationale, reviewer, date, and limitations |

The reported preliminary ranking is not a verified result: the advisor
explicitly questions whether the correct data were selected, and no numeric
metric values or executable analysis accompany the chat.

## Update after receiving the three figures

The first two attached figures are treated as the advisor's and the third
as the author's, following their order and the user's description.

The first figure contains nine terminal/phase panels with right-tailed
histograms. It labels gamma as the best tested fit in seven panels and
lognormal at the opposite terminal in phases B and C. These are the figure's
reported selections, not independently reproduced model-ranking results.
The selected curves visually follow the asymmetry better than the dashed
normal curves, but still miss some histogram peaks and shoulders. The figure
does not disclose the selection criterion, sample size, scenario, fitted
parameters, or voltage base. These must accompany the final evidence.

The second figure shows normal curves over nine similarly shaped histograms,
with means from 1.123 to 1.190 p.u. and standard deviations from 0.087 to
0.135 p.u. The narrow concentration near the lower observed range and the
right tail explain the visible mismatch with a symmetric approximation.
Visual agreement between the first two sets of bars suggests related data,
but cannot establish identical source files or preprocessing.

The third figure explicitly shows 1,000 shots and only phase A:

| Node | Visible pattern | Interpretation limit |
| --- | --- | --- |
| T_MANA | Main peak near 1.2 p.u., tail to the right | A right-skewed family is a candidate, not a validated fit |
| 1_2LTA | Broad profile with elevated regions near 1.5 and 1.9 p.u. | Possible multiple modes; check raw values and bin sensitivity before asserting distinct populations |
| T_OPOA | Strong concentration near 1.8 p.u., tail toward lower voltages | Do not extrapolate the advisor's right-skewed fits to this panel |

The third figure reports frequencies, whereas the first two report density.
For equal-width bins, density equals count divided by sample size and bin
width. This changes bar heights, not the underlying skew direction or peak
positions when observations and bin edges are identical. Different binning
can change apparent modes. Density above one is not probability above one;
probability corresponds to area over an interval.

No attached figure establishes that all three use the same scenario,
source, base, exclusions, or bin boundaries. The first two appear compatible
with lower-voltage CRPI results and the third with SRPI patterns, but this is
only a hypothesis and must not be used as a source label. Verify provenance
before comparing them. A voltage-base change alone rescales values and does
not reverse skewness.

Immediate next deliverable: reproduce the advisor's two distribution figures
from identified inputs and export the selection criterion and fitted
parameters. Then repeat the same comparison separately for the declared
project groups. Keep empirical exceedance primary even when every candidate
parametric model is inadequate. These figures contain no clustering labels
or Silhouette/Davies-Bouldin values, so clustering-validation work remains
pending. No new algorithms or mixture models are required solely because
one histogram suggests more than one mode.

## What the article supports

Source: Orlando P. Hevia, *Graficos estadisticos con el GTPPLOT*, supplied
[PDF](../2000-N4-Estati-1.pdf). Verify publication metadata before adding its
bibliography entry; the filename alone does not establish venue or date.

- Pages 1-2: ATP generates peak-frequency tables; GTPPLOT reads those tables.
  A grouped maximum still contributes one observation per energization,
  not one observation for every phase in the group.
- Page 2: frequency bins and cumulative counts support probability checks.
  The terms `Grouped data` and `Ungrouped data` distinguish binned and
  original moments; they do not denote machine-learning clusters.
- Pages 5-6: distinguish empirical exceedance plots from the separate
  formula `X_2% = mean + 2.0537494 * standard_deviation`. The latter uses
  the normal 98th-percentile multiplier and is not distribution-free.
- Pages 6-10: histograms and exceedance plots are appropriate presentation
  references. Their appearance is not a target distribution for this LT.

The article does not validate gamma/lognormal fits, clustering algorithms,
or a rule for distinguishing physical extremes from numerical artifacts.
Its example electrical system need not reproduce the project's histogram.
Exact article-case reproduction is an optional software benchmark unless
the thesis explicitly promises replication of that experiment.

## Current repository evidence

The manuscript already contains Methodology, Results, and Conclusion.
The older scientific status review must not be used as current chapter status.

Direct reads of `results/defense-evidence/v1/sources/` found:

| Artifact | Observed state | Implication |
| --- | --- | --- |
| statistical_evidence.csv | 90 rows, all marked valid | Reuse existing probability evidence after final provenance check |
| distribution_adequacy.csv | 88 rejected and 2 not-rejected normality decisions | Gaussian fit cannot be the general inferential foundation |
| probability_reconciliation.csv | 1,151 rows, all marked valid | Existing ATP reconciliation is substantial evidence |
| technical_review.csv | Five unresolved cases | No completed causal review is available |
| package_status.json | Incomplete; electrical review missing | Current acceptance contract is stricter than the advisor's proposed screening scope |

`src/services/distribution_adequacy.py` evaluates Gaussian adequacy and MAD.
Searches in source, tests, manuscript, and bibliography did not locate an
implemented gamma/lognormal comparison or Silhouette/Davies-Bouldin study.
Those results cannot be inferred from the advisor's omitted images.

The current `cluster_hierarchical()` uses terminal-local, one-dimensional
single-linkage gaps to select an upper tail. The plotted dendrogram uses
global Ward linkage. These are different procedures. Define which partition
the comparison assesses and align captions, parameters, and exported labels.
The hierarchy is not documented as a method in the inspected manuscript.

## Ordered completion plan

### 1. Freeze the experimental question and dataset

Use the existing accepted data lineage and document scenario, terminal,
phase, voltage type, voltage base, peak window, event operator, and exclusions.
Use all technically valid observations for primary probability estimation;
do not remove observations merely because a clustering method flags them.
Keep each terminal/phase/scenario separate unless a joint event is explicitly
defined. Multiple phases from one run are not independent energizations.

Start with the advisor's two named subsets. Then cover the declared thesis
matrix or justify a smaller representative matrix before inspecting rankings.
The existing package covers 90 scenario/sample-size/terminal/phase groups.

### 2. Finalize empirical probability evidence

For each declared event, report `k/n`, Wilson 95% interval, threshold, units,
and excluded-run count. Plot empirical exceedance over the observed range,
not only at 2.3 p.u., where the manuscript reports no exceedances.
Keep 2.3 p.u. if technically justified; do not change the physical model or
threshold just to obtain nonzero events. Empirical upper quantiles can provide
additional description, with the chosen quantile convention documented.

Check ATP bin edges and equality cases explicitly: a column headed `.GE.`
cannot be equated silently with a raw-data strict `>` count. If only binned
values are available, an interior-bin threshold does not have an exact raw
event count. Preserve existing reconciliation evidence and document scope.

Zero observed events is not zero underlying probability. For 10,000
independent valid runs and zero events, the two-sided Wilson 95% upper
endpoint is approximately 0.0384%. Do not pool different phases and
terminals to claim this uncertainty for a single event definition.

### 3. Compare distributions without forcing an acceptable fit

Fit normal, gamma, and lognormal to the same unfiltered valid peaks within
each declared group. Record parameter estimates, support, location policy,
fitting method, failures, and software versions. Check whether positive
support and skew direction make the proposed families plausible; positive
voltages alone do not imply gamma or lognormal adequacy.

Recommended evidence: common-bin histogram with densities, empirical and
fitted exceedance curves, Q-Q diagnostics, and AIC or BIC using the same raw
observations and explicit parameter counts. Add a goodness-of-fit procedure
that accounts for estimated parameters, such as parametric Monte Carlo
with refitting. Do not apply an unadjusted fixed-parameter KS interpretation
after estimating parameters from the same sample.

The manuscript reports negative skewness in the SRPI reference group.
Ordinary positive-scale gamma and lognormal families are right-skewed;
their superiority cannot be assumed across all groups. All three models
may be inadequate. That is an acceptable result; empirical probability
remains usable. A relative fit improvement does not validate rare-tail
extrapolation outside the data.

### 4. Evaluate clustering quality and selection stability

Compare methods on identical observations, features, scaling, and distance
definitions within each group. Record cluster counts and sizes, singleton
groups, candidate counts, noise fraction, seeds, and parameters.

Silhouette is better when higher; Davies-Bouldin is better when lower.
They describe geometry, not detection accuracy or electrical truth. Do not
require a universal cutoff or unanimous winner. Discuss conflicting rankings
in terms of cluster size, compactness, separation, and the screening goal.

Mark metrics not applicable when the valid partition lacks the required
number of labels (between 2 and n-1). For DBSCAN, predeclare noise handling;
noise points are not naturally one coherent extra cluster. If noise is
excluded, report retained sample count and avoid presenting scores computed
on different subsets as directly comparable. Record any sampled Silhouette
calculation and its seed for large datasets.

Add limited seed and parameter sensitivity and run-level resampling.
Evaluate candidate-set stability on matching retained observations; unrelated
simulation IDs from separate campaigns cannot be matched directly.

### 5. Review usefulness separately from electrical causation

Prepare a compact review packet for Braulio or another qualified reviewer:
flagged and unflagged controls, method disagreements, original LIS location,
voltage, terminal, phase, switching information, and peer observations.
Ask whether each case deserves further technical analysis, with rationale,
not whether a clustering label proves an ATP fault. Record selection policy,
reviewer, date, and unresolved cases; avoid claiming population-wide accuracy
from a small purposive sample.

Waveforms and fixed-switching reruns with smaller time steps belong to the
stronger claim of physical/numerical cause. If that claim remains outside
scope, request advisor agreement to accept statistical screening and record
causal validation as a limitation. Do not mark unresolved cases resolved or
silently change the existing package's causal acceptance contract.

Existing synthetic precision/recall/F1 results can remain supplementary,
clearly restricted to known injected perturbations. They are not clustering
quality measures or accuracy on real ATP numerical errors. A larger synthetic
benchmark is not requested by the chat and is not the immediate priority.

### 6. Align manuscript, artifacts, and acceptance

Update theory, methodology, results, discussion, and conclusion together:
empirical exceedance primary; gamma/lognormal comparative; internal indices
for grouping; expert review for selection usefulness; causal limits explicit.
Document the actual hierarchical procedure if retained. Add verified article
and metric references. Keep all authored manuscript prose in Brazilian
Portuguese, as required by project instructions.

Reconcile the older validation plans with the agreed acceptance scope.
The current manuscript calls missing causal review a mandatory validation
gap despite a research question limited to selecting candidates. Resolve
this discrepancy explicitly with the advisor rather than treating technical
causal validation as an automatic prerequisite for academic completion.

Regenerate final tables and figures from one frozen configuration and record
input hashes, code revision, dependencies, commands, and output hashes.
If implementation changes are made, run the project-prescribed `task format`,
`task lint`, and `task test` before committing. Compile and visually inspect
the final thesis; trace every conclusion to a table, figure, or review record.

## Minimum reviewable completion package

- Frozen scope and event definitions accepted by the advisor.
- Existing extraction/base/integrity evidence linked to final inputs.
- Empirical probability table, intervals, and exceedance plots.
- Normal/gamma/lognormal comparison with honest adequacy decisions.
- Silhouette/Davies-Bouldin table, applicability notes, and stability evidence.
- Technical usefulness review, or an explicit accepted limitation if absent.
- Updated manuscript and reproducible final artifact manifest.

Completion does not require normal data, nonzero threshold exceedances,
one method winning every metric, or confirmed ATP numerical errors when
causal classification is excluded from the approved thesis scope.

## Supporting method references

### Existing occurrence-probability figure

Follow-up source inspection found that `plot_occurrence_probabilities()` in
`src/services/visualization.py` already presents empirical strict-threshold
probability with Wilson intervals. `run_pipeline()` computes its input via
`summarize_statistical_evidence()` on validated observations before clustering.
Thus, clustering flags do not remove candidate extremes from this estimate.

The saved 1,000-run configuration selects SRPI, phase A, three terminals,
112677 V base, and a 2.3 p.u. threshold. The saved figure and evidence CSV
show zero exceedances out of 1,000 for each terminal. The two-sided Wilson
95% upper endpoint is approximately 0.3827%, which is nearly invisible on
the function's fixed 0-100% vertical axis. A narrower explicitly labelled
axis would improve readability without changing the probability estimate.

Distinguish three questions:

- Fixed-threshold bars: how often does the peak exceed a declared limit?
- Bin probabilities: how often does the peak fall inside a declared range?
- Empirical survival curve: how does exceedance vary with the limit?

None assigns a probability to recurrence of an entire simulated physical
case. Each concerns a voltage event under the simulation's input model.
For the thesis, retain threshold bars as a summary and use empirical
survival curves for the full observed voltage range. Histogram frequencies
can be divided by group count to express bin probability, with boundaries
explicitly defined. Do not interpret fitted density height as probability.

Source inspection also found an unresolved boundary defect in
`plot_exceedance_curve()`: it labels the ordinate `P(X > x)` but calculates
`(n - rank + 1) / n`. For distinct sorted observations this includes the
current observation; for ties it assigns different ordinates to identical
thresholds. For example, values [1, 2, 3] produce [1, 2/3, 1/3], whereas
strict exceedance at those values is [2/3, 1/3, 0]. A corrected curve should
evaluate counts of strictly greater values at unique thresholds, preserving
consistent tie handling. It should also remain available without a Gaussian
fit; the current loop skips a terminal if that fit is absent.

The bar figure itself does not have this rank-count defect: its source
counts `value > threshold` directly. Its labels identify only terminal and
phase, so combined scenarios or sample sizes would require explicit facets
or expanded labels; a single title also assumes a common threshold/unit.
These are scoped follow-up implementation items, not changes made during
this analysis. No code or generated scientific results were modified.

- [Silhouette definition and applicability](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
- [Davies-Bouldin definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.davies_bouldin_score.html)
- [SciPy goodness-of-fit with estimated parameters](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.goodness_of_fit.html)
- [Probability prerequisites](probability_experiment_prerequisites.md)
- [Existing defense plan](defense_validation_plan.md)
- [Hierarchical implementation and metric caveats](hierarchical-clustering-validation-metrics.md)

The older plans remain useful evidence, but their broader detector-validation
requirements are not a literal interpretation of the supplied advisor chat.
