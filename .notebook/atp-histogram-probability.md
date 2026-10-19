# ATP Histogram Probability
> ATP bins and current Matplotlib bins use different contracts

Entry: `src/services/visualization.py:plot_overvoltage_histogram()` (L177-233)

Legacy helper: `plot_overvoltage_histogram()` retains shared 20-bin step
histograms. The configured pipeline now uses the advisor-style density
panels described in the follow-up below.

GTPPLOT panels:
`src/services/visualization.py:plot_gtpplot_histograms()`
- Separate terminal-phase panels; fixed 0.05 p.u. compartments
- ATP boundary rule: `lower < value <= upper`
- Output: `gtpplot_histograms.png`
- Individual tables only; no grouped `SUMMARY` maximum
- All 258 inspected phase-A bins across 50-10,000 runs match `case.lis`
- Stable 10,000-run modes: T_MAN 1.20, 1_2LT 1.90, T_OPO 1.80 p.u.
- Analysis: `doc/generated_case_plots_analysis.md`

ATP source: `src/parser/statistical_distribution.py` (L38-126)
- One table per node-phase; denominator from `NENERG`
- Existing `case.lis` files declare `AINCR = 0.050 p.u.`
- ATP frequencies use fixed compartments; current plot derives 20 shared edges
- GTPPLOT example: separate filled panels, including grouped `SUMMARY`

Probability: `src/services/statistical_evidence.py` (L57-213)
- Direct event uses strict `value_pu > threshold`
- Reports occurrence count, denominator, and 95% Wilson interval
- Zero observations != proven zero probability

Analysis: `doc/gtpplot_histogram_probability_analysis.md`

Follow-up: occurrence and exceedance figures (2026-10-17)
- `visualization.py:plot_occurrence_probabilities()` uses direct-count evidence
  computed before clustering by `pipeline.py:run_pipeline()`.
- Saved SRPI/1,000/phase-A figure: 0/1,000 above 2.3 p.u. at each terminal;
  fixed 0-100% axis obscures Wilson upper endpoints near 0.3827%.
- `visualization.py:plot_exceedance_curve()` has unresolved strict-boundary
  mismatch: `(n-rank+1)/n` includes current point and mishandles ties.
- That curve also skips empirical points when Gaussian fit is absent.
- Detailed interpretation: `doc/advisor_article_completion_assessment.md`.

Updated: 2026-10-17

Follow-up: advisor-style densities (2026-10-17)
- `pipeline.py:run_pipeline()` now validates A/B/C separately from the
  configured single-phase analysis and replaces `overvoltage_histogram.png`
  with terminal-row / phase-column density panels.
- `distribution_histograms.py:compare_distributions()` fits normal, gamma,
  lognormal by MLE with estimated location; AIC selects relative fit only.
- New CSVs: `histogram_observations.csv`, `distribution_comparison.csv`.
- Twenty local equal-width density bins differ from fixed ATP compartments;
  `plot_gtpplot_histograms()` remains unchanged.
- Existing five case configs select SRPI, not every nested contingency.
- Reproduction and limitations: `doc/advisor_style_histograms.md`.
