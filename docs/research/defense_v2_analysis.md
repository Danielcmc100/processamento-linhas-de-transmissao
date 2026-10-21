# Defense evidence v2: comparative clustering analysis

## Scope

The canonical manuscript remains `doc/main.tex` (Brazilian Portuguese).
The v2 evidence is regenerated from the ten canonical ATP sources, preserving
v1 and its data. The comparison covers 90 scenario-size-terminal-phase groups
and three methods, producing 270 internal-metric records. The five source
sizes are 50, 100, 200, 1,000 and 10,000 energizations.

## Interpretation

- K-Means fixes two clusters. Internal scores describe the imposed partition;
  they do not prove distinct physical populations or numerical errors.
- DBSCAN excludes noise before internal evaluation. A detector can be
  applicable while its partition has only one retained cluster, leaving
  Silhouette and Davies–Bouldin unavailable.
- Hierarchical selection uses terminal-local upper-tail single-linkage gaps,
  not the global Ward dendrogram exported for exploratory visualization.
  The Ward display aggregates its leaves to at most 30 branches while
  retaining every observation in the linkage; this avoids plotting 30,000
  labels for each large run.
  Its singleton upper groups are excluded by the repository's metric policy.
- Higher Silhouette and lower Davies–Bouldin favor geometric separation.
  Coverage, noise exclusion and differing method objectives prevent a naive
  universal ranking. Missing scores remain missing rather than becoming zero.
- Source independence and nesting are unestablished. Changes across sample
  sizes are descriptive, not an isolated causal effect of sample count.

## Quantitative findings

Internal metrics are applicable in 90/90 K-Means partitions, 4/90 DBSCAN
partitions and 6/90 hierarchical partitions. DBSCAN has eligible partitions
only at N=50; all methods except K-Means have unavailable scores at N=10,000.
For SRPI, median K-Means Silhouette changes from 0.6491 (N=50) to 0.6258
(N=10,000), while median Davies–Bouldin rises from 0.4499 to 0.5032.

For CRPI, T_OPO, phase A, N=200, K-Means has Silhouette 0.7127 and DB 0.4065;
hierarchical selection has Silhouette 0.5444 and DB 0.3182. The indices prefer
different partitions even on the same 200 observations.

Relative AIC selects gamma/lognormal in 27/18 CRPI groups, and
normal/gamma/lognormal in 29/13/3 SRPI groups. All 270 family fits are retained
without duplicating their three-phase summaries across pipeline phase runs.

## Probability and future validation

Anderson–Darling rejects normality in 88 of 90 groups. Relative AIC selection
among normal, gamma and lognormal fits can vary by measurement group; it is
not a goodness-of-fit test. Rejecting normality does not establish that no
probability distribution exists, or that each individual measurement has a
unique family. Empirical exceedance remains computable. A single common
parametric reference cannot validate whether flagged events are physical or
numerical; event rarity alone cannot establish their cause.

`2000-N4-Estati-1.pdf` is Orlando P. Hevia's *Gráficos estadísticos con el
GTPPLOT*. The PDF is undated, so the bibliography avoids inferring a
publication date from its filename. It explains individual and grouped peak
tabulations and the distinction between switching-time inputs and peak-voltage
outputs. Its electrical case is not ground truth for the project's cases.

Expert electrical review, waveforms and comparable reruns are future work,
outside the thesis's comparative computational scope. The inherited evidence
package status remains incomplete for that external causal layer. No
candidate is automatically removed or called a confirmed ATP numerical error.

## Reproduction and document build

```sh
uv run python -m scripts.build_defense_evidence --output results/defense-evidence/v2
uv run python -m scripts.prepare_defense_document
just build
```

The generator rejects nonempty output unless `--overwrite` is explicit.
`doc/` contains only the standalone thesis compilation inputs. The root `justfile` provides build
commands. Research notes, historical audit evidence and reference
material live under `docs/`. `doc/evidence/v2/` contains only referenced
LaTeX tables and figures; full generated sources remain in `results/`.
Generated large tables use paginated landscape layouts to prevent inherited
horizontal and vertical overflow.

## Final verification

- 309 tests passed; Ruff formatting/lint and BasedPyright passed.
- All 10 canonical source hashes and 609 generated output hashes matched the
  v2 manifest. Recorded implementation hashes also matched current files.
- All 270 comparison scopes are unique, with 90 records per method.
- The 90 statistical-evidence rows are identical to v1; no source-data or
  statistical-baseline change was introduced by the comparison extension.
- Normality rejection count (88/90) and relative model selection count
  (90 selections from 270 fits) were checked against saved CSV sources.
- `make -C doc` generated an 80-page PDF without unresolved citations,
  unresolved references, overfull boxes or the intermediate table-splitting
  warning observed during layout iteration. Representative final table,
  figure and review pages were visually inspected.
- A fresh copy of `doc/`, excluding its generated `build/`, compiled under
  `/tmp/` without any repository input paths. Its extracted PDF text matched
  the canonical build exactly. The Dockerfile declares dependencies; the
  container image itself was not built during this verification.

## Template asset preservation correction

Restored `doc/imagens/UNIFESO.png`, `doc/imagens/dbscam.jpg`,
`doc/figmatlab.jpg` and `doc/fluxo.png` to their original paths. Each file
was checked byte-for-byte against HEAD. Template assets remain part of
`doc/` even when not referenced by the active manuscript. Research notes
and audit records retain their reorganized locations under `docs/`.

## Build command migration

Replaced `doc/Makefile` and `doc/Dockerfile` with the root `justfile`. The
`build` and `clean` recipes preserve the latexmk flags and output directory.
`install-deps` retains the Debian/Ubuntu TeX dependency list. Historical
build verification above records the commands used before this migration.
