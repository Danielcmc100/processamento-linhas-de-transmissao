# Thesis Figure Coherence Validation

## T10.1 — Conceptual and electrical-model figures (2026-10-28)

Status: complete. Scope: READ-10 conceptual/model figures and TODOS REQ-04.
The author authorized sequential sub-agent implementation using local tools.
No Python code, scientific evidence package, experiment, raw input or image
asset changed. Existing changes in TODOS.md and staged/unstaged tasks.md were
not included in this task.

### Ownership and preservation

The previous `imagens/fluxo.png` overview was assessed directly: it described
`.OUT` output, omitted the implemented validation/analysis layers and repeated
an overview outside methodology. Its inclusion was replaced, its original
bytes retained. Exactly one `fig:fluxograma_atp` definition now owns the
implemented workflow near the opening of `chap:methodology`. Theory points
forward through automatic references. Existing TikZ supplies vector text and
arrows; local skill-directory search found no mermaid-studio installation.
No second diagram framework or dependency was introduced.

The retained illustrations have distinct purposes:

| Stable label | Purpose | Physical PDF page / printed page |
| --- | --- | --- |
| `fig:linha_colqui` | Cited example of a transient line model, not this experiment | 22 / 21 |
| `fig:nuvem-clusters-anomalias` | Point positions and centroid concept | 24 / 23 |
| `fig:kmeans-mahon` | Effect of separation in synthetic groups | 28 / 27 |
| `fig:dbscan-comparacao` | Density versus proximity in synthetic spatial examples | 29 / 28 |
| `fig:equivalente_anafas` | Reduced-network provenance | 32 / 31 |
| `fig:equivalente_atp_draw` | Implementation of that network in ATPDraw | 34 / 33 |
| `fig:modelo_linha` | Actual segment lengths and monitoring positions | 35 / 34 |
| `fig:fluxograma_atp` | Authoritative processing overview | 36 / 35 |

The theoretical examples explicitly describe their two-dimensional,
illustrative nature, distinct purposes and lack of evidential force for the
actual one-dimensional per-terminal/per-phase maximum-voltage analysis.
Thus none is presented as an additional implemented experimental method.
The three electrical-model images remain complementary. ANAFAS/ATPDraw
images use full text width with readable vector legends repeating the bus
identifiers discussed in the prose. The line figure adds a native TikZ inset
showing existing 13.3/26.7/26.7/13.3 km segments and T_MAN/1_2LT/T_OPO
positions, with Portuguese displayed decimals. It introduces no new network
parameter or simulated outcome. Original raster detail remains available in
preserved source assets.

### Semantic checks

The overview includes ATP generation separately from Python processing;
`.lis` input; maximum/time extraction; source/scenario/run/terminal/phase
identity; P.U. conversion; integrity and logged deterministic exclusions;
mean and sample standard deviation; empirical exceedance and Wilson interval;
Gaussian adequacy and its qualified comparison; MAD, K-Means distance and
DBSCAN noise under applicability; descriptive non-voting hierarchical labels;
method/sample-size comparison; controlled synthetic evaluation; sensitivity;
and reproducible outputs. The final dashed box and arrow explicitly identify
pending qualified electrical review and unresolved causal status.
`SIGMAX=3.0` appears only as input switching configuration. Gaussian adequacy
is separated visually and explicitly excluded from detection voting.

The methods and units agree with the existing methodology descriptions and
the accepted project invariants. No claim of verified numerical ATP errors,
automatic physical classification or completed electrical review was added.
Comparison against HEAD confirmed all 44 citation commands and all 14 figure
label definitions preserved (including moved labels), with one workflow label.
`git diff --name-only HEAD -- doc/imagens` returned no changed assets.

### Gates and rendered review

- `just build`: pass; 81-page PDF. Log contains no undefined references or
  citations, multiply-defined labels, missing assets, or overfull boxes.
- `uv run task format`: pass; 172 files unchanged.
- `uv run task lint`: pass.
- Parent-run fresh `uv run task test` baseline: 328 passed in 76.72 seconds.
  No software changed in T10.1; software/publication gates are not required
  by its editorial gate definition.
- `git diff --check`: pass.
- Poppler rendered and visual inspection completed for physical PDF pages
  22, 24, 28, 29, 32, 34, 35 and 36, at 1200–1400 pixels per page.
  Captions, sources, electrical legends and new vector diagram were checked
  for clipping, readable text and arrows, scope, interpretation and references.
  The methodology overview fits on its opening page together with its
  introduction; no duplicate overview remains in theory.

Whole-document float integration and residual paragraph splits remain T12.
In particular, the existing floating line-model figure can interrupt the
following model-description paragraph. This task does not claim final layout
acceptance, nor change the pending T10.2–T10.4 statistical figures.


## T10.2 — Comparable distribution and Q-Q figures (2026-10-28)

Assumptions and ownership: current v4 scientific evidence remains authoritative;
no simulation or analysis experiment is repeated. `plot_distribution_qq()`
owns histogram/Q-Q presentation; the builder's extracted
`_generate_distribution_figures()` supplies the two-scenario reference scope.
The manuscript owns interpretation and captions. No task-list or TODOS edit
belongs to this implementation.

- Both scenarios retain all 10,000 observations for T_OPO, phase A, their
  saved Gaussian parameters and saved Anderson-Darling decisions. Shared
  histogram edges derive from the combined observed range solely for display;
  empirical densities and fitted parameters remain scenario-specific. Histogram
  x/y and Q-Q x/y limits match across scenarios. No scientific groups are pooled.
- The distant 2.3 P.U. threshold does not expand the histogram axis. Its note
  explicitly says it lies outside the window and reports 0/10,000 strict
  exceedances for each scenario. Portuguese adequacy, concise headings, scope
  and labels replace mixed-language decisions and duplicated method/status
  metadata. Captions explain shared bins/scales and the off-window threshold.
- Printed-size visual review initially found the histogram legend covering
  a peak. Short labels and placement opposite the fitted mean expose both
  peaks. Final physical PDF pages 53–54 (printed 52–53) were rendered at
  1,600 pixels and inspected: both panels, legends, notes, units and captions
  are readable, without clipping or overlap. Both figures use full text width.

### Regression and publication proof

- Parent's fresh pre-change baseline: 328 tests passed in 76.72 seconds.
  New comparison regression failed before implementation (1 failed/9 passed),
  then passed. Unit assertions cover bins, four corresponding axis limits,
  Portuguese adequacy, units and the explicit off-window exceedance note.
  A builder integration test confirms matching scenario export scope/limits.
- `uv run task format` and `uv run task lint` pass; typecheck reports zero
  errors/warnings/notes. Full `uv run task test`: 330 passed in 77.45 seconds.
  After final legend/number styling, focused tests were rerun: 11 passed in
  2.77 seconds; format and typecheck pass. No test was removed or skipped.
- `scripts/replay_defense_figures.py` publishes presentation-only v5 from
  immutable v4. It refuses an existing destination through `copytree`, verifies
  inherited output hashes, uses saved observations/adequacy and checks that
  only distribution PNG/SVG presentation files change. Manifest records the
  replay command, inherited provenance, implementation hashes, changed paths
  and `experiments_rerun: false`. Intermediate unpublished v5 attempts were
  discarded while correcting visual details; final v5 is the validated result.
- Exactly four artifacts differ from v4: distribution PNG and SVG for each
  scenario. All 290 scientific CSV files retain identical bytes, schemas and
  rows; all tables and non-distribution figures retain identical bytes.
  All 609 v5 output hashes and ten source hashes pass. Package status remains
  incomplete with electrical review unresolved.
- Historical v1–v4 output records and current v5 records were each rechecked
  against their manifests, including raw-source hashes: 2,896 unique referenced
  paths pass (2,886 non-manifest package outputs plus ten raw source paths).
  The five package trees contain 2,891 files including five manifests. This
  differs from T9's 4,353-file preservation snapshot because this check counts
  manifest-referenced paths, not every additional historical/audit file.
- All eleven manuscript evidence references now use v5 and match package
  bytes. Old manuscript assets and original input/template files remain.
  `just build` passes, 81 pages, with no actual LaTeX warnings, missing assets,
  unresolved references/citations or overfull boxes. Whole-document placement
  remains T12; T10.3 and T10.4 retain ownership of their figures.

No specification deviation. Reproduction:
`uv run python -m scripts.replay_defense_figures --source
results/defense-evidence/v4 --output results/defense-evidence/v5`
(requires a fresh destination), followed by the existing document copier and
`just build`.


## T10.3 — Comparable geometric-index figures (2026-10-28)

Status: complete. Assumption: saved v5 clustering metrics remain authoritative;
only their presentation changes. `export_clustering_comparison()` retains CSV
and table ownership and now calls `export_clustering_figures()`. This extracted
owner accepts saved metrics directly, so presentation replay does not rerun
clustering, regenerate tables, or repeat any experiment. The manuscript owns
captions and explicit distinction from the nine-group summary table.

### Acceptance and regression proof

- Both reference figures select only T_OPO, phase A, across the five sample
  sizes. Each corresponding metric shares its y limits across SRPI and CRPI;
  both x axes use the same logarithmic scale, limits and explicit N ticks.
  Fixed color, marker and line styles preserve method identity across panels.
- Non-applicable or missing/non-finite scores become gaps, never zeroes.
  Only methods with at least one valid score enter the legend. Per-panel
  notes name methods with unavailable scores and report affected N counts.
  In the actual reference group DBSCAN has no geometric score at all five
  sizes in either scenario and therefore has no plotted curve or legend key.
  Hierarchical scores are absent at all five SRPI sizes and at three CRPI
  sizes; the two valid CRPI points remain visible. These are geometric-score
  applicability statements, not claims about candidate-detector execution.
- Both captions explain shared axes/styles, unavailable points, valid-only
  legends and the restricted terminal/phase scope, explicitly contrasting it
  with Table `tab:cluster-summary`'s medians across nine terminal-phase groups.
- RED: new reference-plot regression failed before the extracted owner existed
  (1 failed, 2 passed). GREEN: three focused tests pass. Assertions cover shared
  axes, styles, reference-group filtering, a missing middle score retained as
  a gap, missing-method notes, no fictitious DBSCAN legend key and scope.
  Existing export integration still verifies saved records, nine-group
  applicability counts, null metrics, retained noise counts and generated PNG.
  No test was removed, weakened or skipped; final type adaptation uses dynamic
  access to Figure text because installed Matplotlib stubs omit that member.

### Software, publication and editorial gates

- `uv run task format`, `uv run task lint` and `uv run task typecheck`: pass;
  typecheck has zero errors, warnings or notes. Full `uv run task test`:
  331 passed in 81.05 seconds, versus the latest 330-test baseline.
  Final font-sizing and stub-access adjustment: focused suite rerun,
  3 passed in 2.44 seconds; format/lint/typecheck pass.
- Extended `scripts/replay_defense_figures.py` with an explicit `--figures`
  choice, retaining distribution as its default. Clustering replay invokes
  only the extracted figure owner and records its implementation hash.
  Presentation-only v6 derives from immutable v5. Exactly four files change:
  clustering PNG/SVG for CRPI/SRPI. All 290 CSV files preserve exact bytes,
  schemas and row counts; tables and every non-clustering figure are unchanged.
  All 609 current output hashes and ten raw-source hashes pass verification.
  Historical v1–v5 and current v6 manifests were checked: 3,505 unique
  manifest-referenced source/output paths pass. This uses the same counting
  scope as T10.2, not the broader arbitrary-file snapshot used in T9.
- All eleven manuscript references now use v6; copied assets match package
  bytes. Historical manuscript assets and raw/template files remain preserved.
  Package technical review stays incomplete, with no new causal conclusion.
- `just build`: pass, 81 pages; no actual undefined references/citations,
  duplicate-label warnings, missing assets or overfull boxes. Final physical
  pages 58–59 (printed 57–58) rendered at 1,600 pixels and visually inspected.
  Enlarged text after initial printed-size inspection; final panels show all
  five N ticks, shared metric ranges, separated notes and readable legends,
  without clipping or overlap. Whole-document float integration remains T12.
- `git diff --check`: pass. Existing TODOS.md and staged/unstaged task-list
  edits remain outside this commit. No specification deviation. No notebook
  entry added: this report already records the reusable replay/plot ownership.

Reproduction (fresh destination):
`uv run python -m scripts.replay_defense_figures --source
results/defense-evidence/v5 --output results/defense-evidence/v6
--figures clustering`, then `uv run python -m
scripts.prepare_defense_document` and `just build`.
