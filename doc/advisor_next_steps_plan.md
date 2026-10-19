# Advisor-aligned completion plan

Date: 2026-10-17.

## Basis and limits

Sources: [advisor chat](../chat.txt),
[ATP probability notes](../.notebook/atp-histogram-probability.md), and
[completion assessment](advisor_article_completion_assessment.md).
Project planning files and the existing hierarchical-metrics note were also
read to identify conflicting completion criteria.

This is a document-based plan. Source code, saved result counts, article
claims, and previously reported test results were not independently
revalidated. The chat export contains hidden images; descriptions of those
images come from the prior assessment, not a new visual inspection.
Existing staged and unstaged changes were preserved.

## Recommended research contract

Demonstrate reproducible empirical exceedance estimation and selection of
observations for technical investigation. Compare distribution models and
evaluate grouping geometry without claiming confirmed ATP numerical errors.
Keep automated insulation decisions outside the academic scope.

The advisor explicitly requests empirical exceedance, gamma/lognormal
comparison, and internal clustering metrics. Specialist assessment is
proposed as a possibility. Her exploratory method rankings are hypotheses:
the chat questions input selection and provides no reproducible scores.

Confirm with the advisor whether a usefulness review is required for
completion, or whether its absence can be an explicit limitation. Do not
silently reinterpret the existing causal-validation acceptance contract.
This discussion need not block probability corrections or pilot studies.

## Ordered deliverables

### 1. Freeze a small pilot and its provenance

- Start with CRPI / 50 runs / 1_2LT / phase A and SRPI / 50 runs /
  T_MAN / phase B, the two clustering subsets named in the chat.
- Identify source files, hashes, run IDs, voltage base, phase, terminal,
  exclusions, and exact features. Distribution-image provenance remains a
  separate question; these subsets are not proven image sources.
- Define strict exceedance as `P(V > u)` and count one observation per
  energization for each separately defined terminal-phase event.
- Freeze the final analysis matrix before inspecting model rankings.

Done when: both pilot datasets can be regenerated from explicit inputs;
scenario and phase cannot be confused. Primary probabilities retain all
technically valid peaks, including clustering-flagged extremes.

### 2. Repair and verify empirical exceedance presentation

- First verify whether the documented rank-count defect remains present.
- At each unique threshold, calculate the fraction strictly above it.
  Equal values must share the same probability.
- Keep empirical curves available when no Gaussian fit exists.
- Preserve direct threshold counts and Wilson 95% intervals; make small
  intervals readable with explicit axis limits or a supplementary table.
- Keep ATP histogram boundary semantics distinct from strict exceedance.

Done when: `[1, 2, 3]` yields `[2/3, 1/3, 0]`; `[1, 2, 2, 3]`
yields `[3/4, 1/4, 0]` at unique thresholds `[1, 2, 3]`; empirical
plotting works without a fitted model. Threshold bars and curves agree.
Zero events are reported as `0/n` with uncertainty, never proven zero risk.

### 3. Produce a reproducible distribution comparison

- Fit normal, gamma, and lognormal to identical valid observations within
  each group. Record support, location constraints, fitted parameters,
  parameter count, fitting method, and failures.
- Export common-bin density plots, empirical versus fitted exceedance,
  Q-Q diagnostics, and a predeclared relative criterion such as AIC.
- If making formal adequacy claims, use a goodness-of-fit procedure that
  accounts for estimated parameters, such as Monte Carlo with refitting.
- Do not assume gamma/lognormal wins in negatively skewed SRPI groups.

Done when: each group has traceable fit results and diagnostics. Relative
ranking is distinguished from absolute adequacy; all models may fail.
Empirical probability remains primary, including when fits are inadequate.

### 4. Reproduce clustering evaluation on the two pilot subsets

- Compare K-Means and the actual hierarchical partition on identical
  observations, features, scaling, and distance definitions.
- Resolve the documented difference between the terminal-local gap rule
  and the global Ward dendrogram before describing hierarchical results.
- Export Silhouette, Davies-Bouldin, cluster sizes, candidate IDs,
  parameters, seeds, and applicability status.
- Mark invalid partitions as not applicable; do not fabricate scores.
  If including DBSCAN, declare noise handling and report retained counts.
- Reuse existing sensitivity infrastructure where applicable; add only
  missing seed/parameter checks and candidate-selection stability evidence.

Done when: pilot scores can be reproduced without assuming the advisor's
ranking. Higher Silhouette and lower Davies-Bouldin measure geometry,
not electrical correctness. Conflicting rankings are explained rather than
collapsed into an unsupported universal winner.

### 5. Expand the frozen study and assemble a review packet

- Apply the verified pilot workflow to the declared study matrix, reusing
  existing extraction, reconciliation, and uncertainty evidence after
  checking lineage. Avoid rebuilding already accepted capabilities.
- Prepare a manageable selection of flagged cases, unflagged controls,
  and method disagreements with run IDs and original LIS references.
- Ask Braulio or another qualified reviewer whether each case merits
  further technical investigation; record rationale, reviewer, and date.
- If unavailable, record the limitation and obtain the advisor's scope
  decision. Small purposive reviews do not establish population accuracy.

Done when: all declared groups have outputs or explicit failure reasons;
review status is traceable. Causal claims remain unresolved without suitable
electrical evidence, regardless of internal clustering scores.

### 6. Align the manuscript and completion contract

- Update objectives, methods, results, discussion, and conclusion together.
  Keep authored `doc/main.tex` prose in Brazilian Portuguese.
- Replace any universal Gaussian or 3-sigma inference with the actual
  empirical and comparative method. Do not treat outliers as proven errors.
- After scope agreement, reconcile project state, roadmap, and acceptance
  documents. The old statement that only electrical review remains is
  incomplete relative to the advisor's newer comparative requests.
- Preserve stronger causal validation as unresolved or explicitly deferred;
  do not relabel it as completed by a screening-usefulness review.
- Regenerate final evidence from frozen configuration; record code revision,
  input hashes, dependencies, commands, and output hashes.

Done when: every conclusion points to evidence, tables and figures match
the final inputs, and the thesis compiles and passes visual inspection.
Implementation commits require `task format`, `task lint`, and `task test`.

## First work package

Recommended first implementation: verify/fix strict empirical exceedance,
tie handling, and plotting without a Gaussian fit, with focused regression
tests. Then establish both pilot inputs. These deliverables reduce the risk
of building distribution comparisons on misleading probability plots.

In parallel with that work, discuss only the remaining academic decisions:
the screening claim, specialist-review requirement, and final study matrix.
No new clustering algorithm, mixture model, ATP rerun campaign, or expanded
synthetic benchmark is required solely by the supplied chat.
