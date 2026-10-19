# Advisor-style distribution histograms

Date: 2026-10-17.

## Change and scientific contract

The configured pipeline now writes `overvoltage_histogram.png` as a grid
with one terminal per row and phases A, B and C in separate columns.
The figure uses filled density bars, a dashed fitted normal density, and
an orange density for the lowest-AIC model among normal, gamma and
lognormal. When normal wins, the orange curve overlaps the dashed curve.
Labels remain in English under repository documentation conventions.

Inputs are validated three-phase phase-to-ground peaks from the configured
source, before clustering. The existing single-phase policy still governs
the other statistical and clustering outputs. Histogram observations have
their own CSV, avoiding any implication that phase-A evidence covers B/C.
Three-phase validation must succeed before the pipeline produces figures.

Each panel uses 20 equal-width bins spanning its observed range. NumPy /
Matplotlib intervals are left-closed and right-open, except for the final
bin, which includes its right endpoint. Density is count divided by sample
count and bin width; bar area sums to one. These bins are not ATP's fixed
0.05 p.u. right-closed compartments. The existing GTPPLOT frequency figure
is preserved for that separate comparison.

All three distributions use SciPy maximum likelihood with estimated
location and scale; gamma and lognormal also estimate shape. AIC is
`2 * parameter_count - 2 * log_likelihood`, with parameter counts two,
three and three respectively. Location is not fixed to the minimum observed
voltage or to 1 p.u. Parameters, sample counts, warnings and fit failures
are exported in `distribution_comparison.csv`. Constant groups or fewer
than four observations remain unfitted and still have empirical bars.

Estimated-location fits can be sensitive to sample minima and optimizer
behavior, especially in small samples. AIC provides relative ranking only;
no formal goodness-of-fit conclusion or tail extrapolation is justified by
this figure. No observations are removed to make a family fit better.

## Reproduction and output scope

Run from the repository root:

```bash
uv run python main.py input_files/casos/50-simulacoes/input.json
uv run python main.py input_files/casos/100-simulacoes/input.json
uv run python main.py input_files/casos/200-simulacoes/input.json
uv run python main.py input_files/casos/1000-simulacoes/input.json
uv run python main.py input_files/casos/10000-simulacoes/input.json
```

The five existing configurations select SRPI / CASO-COMPLETO / SDEF and
112677 V phase-to-ground base. They do not select every contingency or CRPI
source stored underneath those directories. Each configured result folder
receives nine panels, 27 model-fit rows, and nine observations per simulation
in `histogram_observations.csv`. Metadata records the histogram policy and
input hashes. Raw LIS files and input configurations remain unchanged.

The reference picture provides a presentation pattern, not identified
source data or fitting settings. This change does not claim exact
reproduction of the advisor's model selections or histogram shapes.

## Verification

- Tests check MLE/AIC values, independent phase groups, one selected model
  per fitted group, degenerate samples, unit histogram area and rejection
  of pooled scenarios.
- Pipeline/report tests check all-phase observation counts and new artifacts.
- `uv run task format` and `uv run task lint` pass.
- `uv run task test`: 305 passed. One existing Matplotlib warning about
  more than 20 open figures also occurred in the baseline test run.
- BasedPyright: zero errors and warnings.
- All five configured runs completed successfully. CSV verification found
  nine groups with the configured sample count and 27 fit rows per folder:
  450, 900, 1,800, 9,000 and 90,000 histogram observations respectively.
- Visual checks of regenerated 50-, 1,000- and 10,000-run panels show readable
  labels, densities and curves. SRPI midpoint and opposite-terminal
  histograms retain their original shapes, unlike the reference picture.
- At 10,000 runs, minimum AIC selects gamma at T_MAN/A and T_MAN/B,
  lognormal at T_MAN/C, and normal at the other six terminal-phase groups.
  The latter selections do not demonstrate normality: the plotted midpoint
  and opposite-terminal densities visibly miss aspects of the histograms.

The existing empirical-exceedance plotting issue documented in the prior
assessment is outside this histogram change and remains unresolved.
