# Thesis Readability and Sigma Correction Tasks

**Status:** All tasks implemented and verified, including T13, T14 and
final integration T12; electrical causal validation remains unresolved
**Specification:** [spec.md](spec.md)
**Scope:** One parent task per original proposal; T7 has five executable
subtasks. Additional figure/table requests are grouped under T10 and T11,
with T13 and T14 owning discussion consolidation and continuous results prose.
T12 owns final integration. Parent tasks are groupings, not extra work.
**Analysis:** `docs/research/thesis_visual_editorial_review.md`
**Editorial refinement (2026-10-28):** `TODOS.md`, REQ-01–REQ-05, takes
precedence over conflicting pending presentation choices in this plan and
older `spec.md` acceptance details. In particular, the four detailed tables
move to appendices and receive prose summaries, not replacement main-text
tables. Completed tasks and their historical evidence remain unchanged.
This update authorizes planning only; no manuscript or software implementation
is performed. Future evidence belongs in `docs/research/`.

| TODOS requirement | Owning tasks | Acceptance focus |
| --- | --- | --- |
| REQ-01 | T11.1–T11.4 | Four appendix tables, prose syntheses, preserved evidence |
| REQ-02 | T14 | Connected results prose; no subsection or deeper headings |
| REQ-03 | T13 | One final discussion, exact title, preserved limitations |
| REQ-04 | T10.1 | Readable methodology overview matching the real pipeline |
| REQ-05 | T12 | Source preservation, resolved references, rendered-PDF review |

## Gates and working rules

- **Editorial gate (E):** `just build`; inspect affected sections and log for
  missing assets or unresolved references/citations. Review the diff for
  preserved meaning, citations, labels, and Brazilian Portuguese prose.
- **Software gate (S):** owning unit/integration tests below, followed by
  `uv run task format`, `uv run task lint`, `uv run task test`, and
  `uv run task typecheck`. Capture a fresh baseline; do not claim historical
  test counts as current. Account for removed detector-specific tests.
- **Publication gate (P):** regenerate into a new directory, verify manifest
  hashes, counts, schemas and tables, copy referenced assets, then run E.
- Co-locate test changes with each software component change. Do not defer
  them to the final document task.
- Use filesystem tools and the loaded TLC skill for all tasks; use CodeNavi
  for software tracing. No external MCP service is required. Confirm the
  execution tool choices with the author before starting implementation.
- No parallel implementation: editorial tasks share `doc/main.tex`; software
  tasks share contracts and generated evidence. Delegate sequential execution
  according to the TLC workflow only after approval.

## Execution order and dependency cross-check

The table is the canonical execution map; dependencies in each task match it.
The sequence avoids edits to shared files being overwritten.

| Task | Depends on | Execution-map predecessor | Check |
| --- | --- | --- | --- |
| T7.1 | None | Start | Match |
| T7.2 | T7.1 | T7.1 | Match |
| T7.3 | T7.2 | T7.2 | Match |
| T7.4 | T7.3 | T7.3 | Match |
| T7.5 | T7.4 | T7.4 | Match |
| T1 | T7.5 | T7.5 | Match |
| T3 | T1 | T1 | Match |
| T4 | T3 | T3 | Match |
| T5 | T4 | T4 | Match |
| T6 | T5 | T5 | Match |
| T9 | T6 | T6 | Match |
| T2 | T9 | T9 | Match |
| T8 | T2 | T2 | Match |
| T10.1 | T8 | T8 | Match |
| T10.2 | T10.1 | T10.1 | Match |
| T10.3 | T10.2 | T10.2 | Match |
| T10.4 | T10.3 | T10.3 | Match |
| T11.1 | T10.4 | T10.4 | Match |
| T11.2 | T11.1 | T11.1 | Match |
| T11.3 | T11.2 | T11.2 | Match |
| T11.4 | T11.3 | T11.3 | Match |
| T13 | T11.4 | T11.4 | Match |
| T14 | T13 | T13 | Match |
| T12 | T14 | T14 | Match |

## T1 — Consolidate repeated limitations (proposal 1)

**Requirement:** READ-01
**What/where:** Give scope and limitations clear ownership in `doc/main.tex`.
**Depends on:** T7.5
**Reuses:** Existing scope, validity-layer, and limitations sections.
**Done when:**
- [x] A section inventory identifies the canonical statement of each limit.
- [x] Repeated boilerplate is removed without losing detector-specific or
  result-specific caveats.
- [x] No statistical result is promoted to a causal electrical conclusion.
**Tests:** Editorial review; no Python layer changed.
**Gate/verify:** E; compare retained caveats against the inventory.
**Completion evidence:** `docs/research/thesis_readability_validation.md`,
T1 section; 79-page build and affected-page visual review pass.

## T2 — Introduce results with the principal findings (proposal 2)

**Requirement:** READ-02
**What/where:** Add a concise opening synthesis in `doc/main.tex` results.
**Depends on:** T9
**Reuses:** Newly published evidence and existing result sections.
**Done when:**
- [x] Validated dataset, exceedance, normality, and clustering applicability
  are summarized before detailed audits.
- [x] Every number matches the current evidence package, not an old example.
**Tests:** Source-to-prose reconciliation; no Python layer changed.
**Gate/verify:** E; record the source table/column for each summary claim.

**Completion evidence (2026-10-28):**
`docs/research/thesis_readability_validation.md`, T2 section; sequential
sub-agent execution, source reconciliation, clean build and rendered-page
review. See that record for current software/publication gates where applicable.

## T3 — Move reproduction details to the appendix (proposal 3)

**Requirement:** READ-03
**What/where:** Relocate audit logistics within `doc/main.tex`.
**Depends on:** T1
**Reuses:** Existing technical-validation appendix and research reports.
**Done when:**
- [x] Commands, detailed paths, file-line references, hashes, dates, and
  correction history have appendix ownership rather than repeated prose.
- [x] Main text retains criteria, tolerances, results, limitations, and the
  electrical derivation of the voltage base.
- [x] Cross-references resolve and no reproduction evidence is lost.
**Tests:** Editorial relocation checklist; no Python layer changed.
**Gate/verify:** E; compare original and relocated technical records.
**Completion evidence:** `docs/research/thesis_readability_validation.md`,
T3 section; relocation inventory, preserved citations/equations/assets and
79-page build with affected-page visual review pass.

## T4 — Split dense theory paragraphs by purpose (proposal 4)

**Requirement:** READ-04
**What/where:** Restructure theory paragraphs in `doc/main.tex`.
**Depends on:** T3
**Reuses:** Existing electrical, visualization, K-Means, and DBSCAN discussion.
**Done when:**
- [x] Definition, literature, limitations, and application have distinct
  paragraph roles where currently mixed.
- [x] Citations remain attached to the claims they support.
- [x] No arbitrary word limit or paragraph split damages logical continuity.
**Tests:** Paragraph-purpose review; no Python layer changed.
**Gate/verify:** E; compare argument and citation coverage before/after.

**Completion evidence:** `docs/research/thesis_readability_validation.md`,
T4 section; purpose inventory, whitespace-normalized source identity and
79-page build with affected theory-page visual review pass.

## T5 — Standardize terms, spelling, and acronyms (proposal 5)

**Requirement:** READ-05
**What/where:** Apply a terminology inventory to `doc/main.tex`.
**Depends on:** T4
**Reuses:** Existing acronyms and symbol lists, actual grouping keys in code.
**Done when:**
- [x] SRPI, CRPI, P.U., MAD, and AIC are defined appropriately.
- [x] Routine, model, candidate, grouping, applicability, and source lineage
  are distinct where necessary and consistent elsewhere.
- [x] Source lineage is defined from actual metadata semantics, not guessed.
- [x] Technical jargon is replaced or defined; centroide spelling is fixed.
**Tests:** Term search and first-use review; no Python layer changed.
**Gate/verify:** E; check prose, captions, and acronym/symbol lists.

**Completion evidence (2026-10-27):**
`docs/research/thesis_readability_validation.md`, T5 section: terminology
inventory, code-grounded lineage semantics, preserved citations/assets/
equations/labels, clean 80-page build and affected-page visual review.
Taskipy format/lint pass; 327 tests pass.

## T6 — Align verb tense with completion status (proposal 6)

**Requirement:** READ-06
**What/where:** Correct procedure and future-work tenses in `doc/main.tex`.
**Depends on:** T5
**Reuses:** Actual execution status and explicitly pending electrical review.
**Done when:**
- [x] Completed experiments use past tense, concepts use present tense, and
  future tense refers only to pending work.
- [x] No editorial change falsely claims an experiment was executed.
**Tests:** Tense/status review; no Python layer changed.
**Gate/verify:** E; reconcile procedural claims with execution evidence.

**Completion evidence (2026-10-28):**
`docs/research/thesis_readability_validation.md`, T6 section; sequential
sub-agent execution, source reconciliation, clean build and rendered-page
review. See that record for current software/publication gates where applicable.

## T7 — Correct three-sigma methods and interpretations (proposal 7)

**Requirement:** READ-07
Execute all five subtasks below; do not implement the parent separately.

### T7.1 — Retire the voltage detector and its comparison contract

**What/where:** Remove `_add_sigma_evidence()` and its call in
`src/services/pipeline.py`; remove the sigma criterion from
`src/services/comparison.py`; update their owning tests.
**Depends on:** None
**Reuses:** Existing MAD, K-Means, DBSCAN applicability and comparison rules.
**Done when:**
- [x] Pipeline does not append sigma detector flags, thresholds, or reasons.
- [x] Comparison requires only the three remaining criteria; hierarchical
  labels remain non-voting and non-applicable methods stay excluded.
- [x] Regression tests cover zero/one/multiple applicable methods, positive
  union, disagreement, deterministic reasons, and unchanged row identity.
- [x] No compatibility switch re-enables the retired detector.
**Tests:** Unit comparison tests and pipeline integration tests in
`tests/test_comparison.py` and `tests/test_pipeline.py`.
**Gate/verify:** S; targeted tests above plus full suite. Intermediate
downstream contract failures must be documented, not suppressed.

### T7.2 — Remove voltage-sigma outputs from statistical summaries and plots

**What/where:** Update `src/services/statistics.py`, `schemas.py`, and
`visualization.py`, their active callers, and owning tests.
**Depends on:** T7.1
**Reuses:** Existing descriptive statistics, Gaussian fit and adequacy tests.
**Done when:**
- [x] `sigma_3_threshold` is absent from active summary schemas and exports.
- [x] Output-voltage sigma screening lines/tables are no longer presented.
- [x] Generic sigma helpers are classified by caller; newly unused helpers
  are removed without removing mean, sample deviation, or Gaussian adequacy.
- [x] MAD calculations and configured ATP switching behavior are unchanged.
**Tests:** `tests/test_statistics.py`, `tests/test_visualization.py`, pipeline
integration, and schema/reporting tests affected by output contracts.
**Gate/verify:** S; assert removed columns/markers and retained statistical
results, including empty, non-finite, and zero-variance cases.

### T7.3 — Align evidence consumers and publication routing

**What/where:** Update `src/services/convergence.py`, `defense_reporting.py`,
reporting consumers, `scripts/build_defense_evidence.py`,
`scripts/prepare_defense_document.py`, and their owning tests as needed.
**Depends on:** T7.2
**Reuses:** Existing evidence generator, manifest, tables, and asset copier.
**Done when:**
- [x] Comparisons, convergence, review selection, and reports consume the
  three-method contract and do not hardcode four detector criteria.
- [x] Publication routes to a new version without overwriting v1/v2.
- [x] The copier resolves the new evidence references; no unnecessary new
  publication framework is introduced.
- [x] Fixture-generated artifacts contain no active voltage-sigma detector
  fields, reasons, or labels; retained Gaussian diagnostics are intact.
**Tests:** Co-located convergence, defense-reporting, evidence-builder,
reproducibility, and asset-copy regression coverage.
**Gate/verify:** S; generate a temporary fixture package and verify its
schemas, votes, manifests, and referenced assets before real-data generation.

### T7.4 — Regenerate evidence without modifying historical inputs

**What/where:** Produce `results/defense-evidence/v3/` from the ten canonical
sources; do not modify `input_files/` or historical v1/v2 packages.
**Depends on:** T7.3
**Reuses:** `scripts.build_defense_evidence` and its source manifest.
**Done when:**
- [x] Run `uv run python -m scripts.build_defense_evidence --output
  results/defense-evidence/v3` into a fresh output directory.
- [x] Input hashes and accepted observation counts match the declared scope;
  candidate, agreement, denominator, convergence, and review counts are
  recalculated rather than copied from v2.
- [x] Every changed/unchanged result is accounted for; missing inputs or
  execution failures block publication instead of mixing evidence versions.
- [x] Electrical review remains unresolved; no synthetic test becomes a
  causal ATP-error label.
**Tests:** Manifest/schema checks and comparison with the previous package.
**Gate/verify:** P's generation/manifest portion; document diff of results.
Manuscript publication and full build occur in T7.5.

### T7.5 — Correct manuscript claims and active project guidance

**What/where:** Update `doc/main.tex`, referenced `doc/evidence/` assets,
`AGENTS.md`, and directly relevant active specs/guidance.
**Depends on:** T7.4
**Reuses:** New evidence, existing methodological structure, historical notes.
**Done when:**
- [x] Remove voltage three-sigma objectives, equations, detector comparisons,
  sensitivity claims, and conclusions; do not merely reword applicability.
- [x] Preserve a source-supported switching-model description where useful.
- [x] Correct Wilson/convergence and MAD/skewness interpretations described
  in READ-07; avoid unsupported causal language.
- [x] Reconcile all affected counts, captions, tables, figures and references
  with v3; run `uv run python -m scripts.prepare_defense_document`.
- [x] Active instructions no longer require the retired detector; older
  requirements are clearly superseded without falsifying historical records.
- [x] Classify remaining sigma references, including plots, generic helpers,
  raw inputs and historical plans. No blanket repository deletion is used.
**Tests:** Editorial and source-to-claim review; asset-copy regression tests
remain with T7.3, not deferred here.
**Gate/verify:** E and complete P; inspect the compiled affected pages.

## T8 — Replace the objective checklist conclusion (proposal 8)

**Requirement:** READ-08
**What/where:** Rewrite the conclusion in `doc/main.tex`.
**Depends on:** T2
**Reuses:** Verified synthesis and scope/limitations sections.
**Done when:**
- [x] Four concise blocks cover contribution, findings, limits, future work.
- [x] Repeated objective-by-objective success declarations are removed.
- [x] No old sigma-detector claim or superseded result returns.
- [x] Review confirms the nine original editorial requirements and build;
  final visual integration is owned by T12.
**Tests:** Editorial checklist and final evidence-to-text review.
**Gate/verify:** E; review the final PDF and record completion evidence.

**Completion evidence (2026-10-28):**
`docs/research/thesis_readability_validation.md`, T8 section; four connected
conclusion paragraphs, READ-01–READ-09 review, clean 80-page build and
rendered-page inspection. Final integration remains assigned to T12.

## T9 — Standardize numbers and simplify table presentation (proposal 9)

**Requirement:** READ-09
**What/where:** Adjust `doc/main.tex` and, if necessary, the owning table
formatters in `src/services/defense_reporting.py` with their tests.
**Depends on:** T6
**Reuses:** Existing detailed evidence tables and full-precision CSV files.
**Done when:**
- [x] Decimal and thousands conventions are consistent in reader-facing text.
- [x] Conversion examples use meaningful display precision; verification
  error is shown where it communicates tolerance better than long decimals.
- [x] Any moved detailed table has a readable main-text summary and a
  resolvable detailed reference, without losing analysis coverage.
- [x] Generated tables are changed in their owner and regenerated, not only
  edited by hand; raw numeric precision is unchanged.
- [x] Mapping Table 1 remains useful and readable; clustering Table 4 retains
  applicability counts, explains NA and nine-group medians, and avoids an
  unjustified ranking. T11 owns the other result-table reductions.
**Tests:** Editorial review; co-located table-formatting regression tests
whenever a Python formatter changes.
**Gate/verify:** E; also S and P if table generation changes. Check widths,
page breaks, appendix placement, captions, and no source rounding.

**Completion evidence (2026-10-28):**
`docs/research/thesis_readability_validation.md`, T9 section; sequential
sub-agent execution, source reconciliation, clean build and rendered-page
review. See that record for current software/publication gates where applicable.

## T10 — Improve figure coherence (additional request)

**Requirement:** READ-10; TODOS REQ-04 through T10.1. Execute the following four subtasks.

### T10.1 — Curate conceptual and electrical-model figures

**What/where:** Review Figures 1–8 in `doc/main.tex` and their source assets.
**Depends on:** T8
**Reuses:** Existing workflow, cited illustrations, and ATP/ANAFAS diagrams.
**Done when:**
- [x] Give each conceptual illustration one distinct purpose; remove or
  relocate redundant main-text inclusions, preserving assets and citations.
- [x] Integrate a readable overview near the opening of `chap:methodology`,
  introduced and interpreted in prose. Assess reuse/adaptation/relocation of
  `fig:fluxograma_atp` (`imagens/fluxo.png`) first; avoid duplicate overviews
  and preserve original assets if replaced. Correct `.OUT` to `.lis`.
- [x] Show extraction of maxima/times, observation identity, P.U. conversion,
  integrity checks/logged exclusions, descriptive statistics and empirical
  probability, Gaussian adequacy, clustering/candidate detection, comparison,
  controlled evaluation, sensitivity, and reproducible evidence. Use readable
  panels if needed; distinguish ATP generation from Python post-processing.
- [x] Show electrical review as pending/future. Keep Gaussian adequacy separate
  from MAD, K-Means distance, and DBSCAN noise under applicability rules;
  hierarchical labels remain descriptive and non-voting. `SIGMAX=3.0` belongs
  to input switching, never output-voltage detection.
- [x] Supply Brazilian Portuguese diagram text and caption, unique label,
  source statement, working reference, and legible final-size text/arrows.
- [x] Explain that 2D schematics are illustrative, not the actual 1D analysis.
- [x] Preserve complementary ANAFAS/ATPDraw/line figures; make discussed bus,
  segment and monitoring labels readable without inventing engineering data.
**Tests:** Asset/citation preservation and semantic/visual review.
**Gate/verify:** E. If redrawing is necessary, check for the mermaid-studio
skill before diagram work; do not introduce a second diagram framework.

### T10.2 — Coordinate histogram and Q–Q scenario figures

**What/where:** Update the distribution-figure owner reached from
`scripts/build_defense_evidence.py:_generate_figures()`, owning tests,
and Figures 9–10 references/captions in `doc/main.tex`.
**Depends on:** T10.1
**Reuses:** Existing distributions, adequacy results, histogram and Q–Q plots.
**Done when:**
- [x] Both scenarios retain histogram and Q–Q evidence with compatible scales
  and bins for the intended comparison; any different scale is explicit.
- [x] The distant threshold is annotated or separated without compressing
  the observed distribution or hiding exceedance information.
- [x] Portuguese labels/status, concise headings and final-size readability
  replace duplicated metadata and mixed-language status.
**Tests:** Co-located plot-content/smoke tests plus visual comparison.
**Gate/verify:** S, P, E; assertions cover plotted scope, units and adequacy.

### T10.3 — Coordinate geometric-index scenario figures

**What/where:** Update the clustering figure owner in the evidence builder,
its tests, and Figures 11–12 captions/layout.
**Depends on:** T10.2
**Reuses:** `clustering_comparison.csv` and existing Silhouette/DB plots.
**Done when:**
- [x] Each corresponding metric uses a common scenario scale and consistent
  method styles; unavailable scores are explicit, never zero-filled.
- [x] A legend does not imply a plotted valid DBSCAN curve where none exists.
- [x] Captions distinguish T_OPO/phase A from Table 4's nine-group medians.
**Tests:** Co-located tests for applicability/missing values and plot scope.
**Gate/verify:** S, P, E; visually compare scenarios at final printed size.

### T10.4 — Make sample-size figures informative and accurate

**What/where:** Update the sample-size figure owner in the evidence builder,
its tests, and Figures 13–14 captions/layout.
**Depends on:** T10.3
**Reuses:** Existing mean, percentile, candidate, probability and Wilson data.
**Done when:**
- [x] Captions match actual panels; show descriptive measures, candidate rate
  and exceedance uncertainty using existing results, or explicitly narrow
  the stated content with an editorial justification.
- [x] Across-N scope is not labeled n=10000; labels are Portuguese.
- [x] Shared corresponding axes reveal small candidate-rate differences;
  zero empirical exceedance is accompanied by uncertainty, not certainty.
- [x] Replace unsupported convergence language with descriptive comparison.
**Tests:** Co-located tests for plotted series, scope labels and interval data.
**Gate/verify:** S, P, E; verify against the regenerated comparison table.

## T11 — Reduce table repetition without losing evidence (additional request)

**Requirement:** READ-11. T9 covers mapping/conversion/clustering tables;
the following four subtasks own the remaining table-specific changes.

### T11.1 — Relocate the detailed probability table

**Requirement:** READ-11; TODOS REQ-01
**What/where:** Relocate `evidence/v3/tables/probability.tex` within
`doc/main.tex` to a clearly titled appendix or appendix section.
**Depends on:** T10.4
**Reuses:** Existing full table, `tab:defesa-probabilidade`, and grouped data.
**Done when:**
- [x] Detailed Table 3 appears exactly once, in the appendix, with all rows,
  caption, label, and provenance preserved; no replacement main-text table.
- [x] Its former inclusion becomes connected prose reporting zero exceedances
  of 2.3 P.U. across 204,300 observations and 90 groups, with Wilson uncertainty.
  Zero events does not imply zero underlying probability.
- [x] Prose references both destination appendix and detailed table through
  labels; denominators remain per group, without pooling or omitted exceptions.
**Tests:** Source-to-prose reconciliation of all 90 rows and relocation review;
no Python change required. If a formatter changes, include its unit tests and
cross-boundary integration tests in this task.
**Gate/verify:** E; S and P only if generated content changes. Verify exactly
one inclusion and complete appendix coverage.

### T11.2 — Relocate the detailed sample-size table

**Requirement:** READ-11; TODOS REQ-01
**What/where:** Relocate `evidence/v3/tables/convergence.tex` within
`doc/main.tex`, retaining `tab:defesa-convergencia`.
**Depends on:** T11.1
**Reuses:** Full comparison data and existing table; T_OPO/phase-A examples.
**Done when:**
- [x] Detailed Table 5 appears exactly once in an appendix, preserving all
  rows, caption, label, and provenance; no ten-row replacement main-text table.
- [x] Its former inclusion becomes prose comparing all five sample sizes under
  the same controls, candidate-rate changes, and shrinking Wilson intervals.
  Reference both appendix and table using labels.
- [x] The largest sample remains an empirical reference, not ground truth;
  sources are not presumed independent or nested. Reference-group examples
  explicitly retain their restricted terminal/phase scope.
- [x] Claims reconcile with full-precision data and Figures 13–14; no analysis
  coverage or qualification disappears.
**Tests:** Relocation and source-to-prose reconciliation; no Python change
required. Include owning unit/integration tests if generation changes.
**Gate/verify:** E; S and P only if generated content changes.

### T11.3 — Relocate the benchmark and restore condition identity

**Requirement:** READ-11; TODOS REQ-01
**What/where:** Relocate `evidence/v3/tables/benchmark.tex` in `doc/main.tex`;
correct presentation in `src/services/defense_reporting.py` and owning tests.
**Depends on:** T11.2
**Reuses:** Existing benchmark source records; do not rerun new experiments.
**Done when:**
- [x] Detailed Table 6 appears exactly once in an appendix, retaining all
  confusion counts, metrics, caption, `tab:defesa-benchmark`, and provenance.
  Its former inclusion becomes prose referencing both appendix and table.
- [x] Summarize intervention families, 1%, 5%, 10% contamination, clean
  baseline, and performance tradeoffs. Restrict findings to tested synthetic
  conditions and the evaluated reference group; do not rerun experiments.
- [x] Add contamination percentage distinct from perturbation intensity.
- [x] Each row identifies its condition and any scenario/group aggregation;
  no three distinct conditions appear to have the same experimental key.
- [x] Translate intervention labels and keep all detailed metric columns
  readable in the appendix; do not introduce a replacement main-text table.
- [x] Avoid a second landscape page containing only the last two rows.
**Tests:** Co-located tests distinguishing 1%, 5%, 10% at fixed intensity,
plus source-to-presentation count/metric checks.
**Gate/verify:** S, P, E; inspect all conditions without inferring them from
true-positive/false-negative counts.

### T11.4 — Relocate pending-review cases with traceability

**Requirement:** READ-11; TODOS REQ-01
**What/where:** Relocate `evidence/v3/tables/technical_review.tex` in
`doc/main.tex`; update its formatter and owning tests as needed.
**Depends on:** T11.3
**Reuses:** Existing selected-case identities and unresolved review evidence.
**Done when:**
- [x] Detailed Table 7 appears exactly once in an appendix, preserving every
  case, caption, `tab:defesa-revisao-tecnica`, and provenance. Main text uses
  prose reporting five causally unresolved cases and missing electrical
  evidence, with automatic references to both appendix and table.
- [x] Show source identifiers with scenario/sample size and a full-path/hash
  mapping; `case.lis` alone is not accepted as a unique source.
- [x] Share repeated unresolved/reviewer/date/justification information in a
  note, preserving row-specific identity, voltage and analytical evidence.
- [x] Mark controls explicitly instead of an unexplained blank evidence cell.
- [x] Describe cases as awaiting electrical review, not completed reviews.
**Tests:** Co-located duplicate-basename, control-label and status-preservation
regression tests; missing source identity blocks misleading publication.
**Gate/verify:** S, P, E; trace each displayed case to its exact input.

## T13 — Consolidate the final discussion

**Requirement:** TODOS REQ-03
**What/where:** Merge the final three active results sections in `doc/main.tex`.
The original 5.10–5.12 numbering is historical; current source order is
5.8–5.10. Identify by `sec:avaliacao-controlada`, `sec:discussao-resultados`,
and `sec:alcance-limitacoes`, including nested `sec:lacunas-pacote` content.
**Depends on:** T11.4
**Reuses:** Existing discussion, evaluation, limitations, and appendix references.
**Done when:**
- [x] One section titled exactly “Discussão acerca dos resultados” replaces
  the three sections, with no retained nested subsection heading.
- [x] Connected paragraphs cover controlled evaluation/sensitivity, selected
  review cases, research objectives, scope/limitations, and future validation,
  in that order. Remove repetition, not substantive evidence.
- [x] Benchmark/review findings reference their appendix tables. Completed
  computational work remains distinct from pending electrical validation;
  stability is not accuracy and synthetic results do not prove ATP errors.
- [x] Preserve meaningful labels or update every use consistently, including
  methodology, conclusion, and appendices; no duplicate/undefined targets.
**Tests:** Section inventory, claim-preservation and cross-reference review;
no Python layer changed.
**Gate/verify:** E; compare all three original sections against merged content.

## T14 — Connect results prose and remove subsection headings

**Requirement:** TODOS REQ-02
**What/where:** Integrate subsection content into results prose in `doc/main.tex`.
**Depends on:** T13
**Reuses:** Existing analytical sections, GTPPLOT and clustering discussions.
**Done when:**
- [x] No active subsection or deeper heading remains in the results chapter.
  Preserve main analytical sections preceding the merged discussion; do not
  flatten the whole chapter or change other chapters' heading structure.
- [x] Integrate GTPPLOT, individual methods, sample-size effects, and causal
  limitations with transitions linking extraction through sample comparison.
- [x] Preserve definitions, citations, figures, numerical evidence, and limits;
  retarget removed-heading references and obsolete section-number wording.
- [x] Prose reads continuously without orphan fragments or a heading replaced
  merely by an isolated bold title.
**Tests:** Heading inventory, citation/content preservation and reading review;
no Python layer changed.
**Gate/verify:** E; inspect complete rendered results chapter and all label uses.

## T12 — Validate final figure/table placement and integration

**Requirement:** READ-12; TODOS REQ-05
**What/where:** Reflow `doc/main.tex` and inspect the complete final PDF after
all editorial and regenerated-asset changes.
**Depends on:** T14
**Reuses:** Existing float controls and the visual-review inventory.
**Done when:**
- [x] Verify REQ-01–REQ-04 against source and rendered PDF: four detailed
  tables only in appendices, each included once, each former location with
  prose and table/appendix references; exact merged title; no results
  subsections; integrated methodology illustration.
- [x] Preserve main-text mapping, P.U. validation, and clustering tables.
  Check contents and lists of figures/tables after renumbering.
- [x] Compare before/after counts, claims, units, accepted P.U. base, Wilson
  intervals, applicability, and unresolved causal conclusions. Preserve raw
  data, experiment outputs, and template assets; do not rerun experiments.
- [x] No isolated trailing line before the ATPDraw figure; first references
  and objects remain in the relevant topic, without inappropriate float drift.
- [x] Reassess the forced break before clustering; do not blanket-apply `[H]`
  or shrink all fonts to hide excessive table width.
- [x] Summary tables use portrait where readable; detailed appendix tables
  preserve header repetition and readable page continuations.
- [x] Inspect every figure/table at final size for clipping, tiny labels,
  captions, units, redundant headings, whitespace and scenario consistency.
- [x] Reconcile opening synthesis, discussion and conclusion with final
  tables/figures; all READ-01–READ-12 and TODOS REQ-01–REQ-05 criteria have recorded verification.
**Tests:** Whole-document rendered-page review and reference/asset checks.
**Gate/verify:** E and P; record final page locations and remaining limitations
in a validation report. A clean LaTeX log alone does not satisfy this task.

## Pre-approval granularity and test co-location checks

| Task(s) | Atomic deliverable | Required proof | Co-location check |
| --- | --- | --- | --- |
| T1 | Ownership of limitations | Editorial/build | No Python layer |
| T2 | Results opening synthesis | Evidence reconciliation/build | No Python layer |
| T3 | Appendix relocation | Preservation/build | No Python layer |
| T4 | Theory paragraph structure | Citation/argument review/build | No Python layer |
| T5 | Terminology inventory application | Search/first-use review/build | No Python layer |
| T6 | Tense/status alignment | Execution-status review/build | No Python layer |
| T7.1 | Three-method comparison contract | Unit + integration | Included in task |
| T7.2 | Sigma-free summary/plot contract | Unit + integration | Included in task |
| T7.3 | Compatible evidence publication | Unit + integration | Included in task |
| T7.4 | New evidence package | Manifest/schema/reconciliation | No production-code change |
| T7.5 | Correct current scientific claims | Source review/build | No deferred software tests |
| T8 | Four-block conclusion | Evidence review/build | No Python layer |
| T9 | Reader-facing numeric presentation | Build + formatter tests if changed | Included conditionally |
| T10.1 | Concept/model figure curation | Citation/semantic review/build | No Python layer unless redraw tooling changes |
| T10.2 | Distribution comparison view | Unit + visual/publication | Included in task |
| T10.3 | Geometric-index comparison view | Unit + visual/publication | Included in task |
| T10.4 | Sample-size comparison view | Unit + visual/publication | Included in task |
| T11.1 | Probability appendix relocation/prose | Editorial; unit/integration if generator changes | Included conditionally |
| T11.2 | Sample-size appendix relocation/prose | Editorial; unit/integration if generator changes | Included conditionally |
| T11.3 | Identifiable benchmark rows | Unit + publication | Included in task |
| T11.4 | Traceable pending-review rows | Unit + publication | Included in task |
| T13 | Consolidated discussion | Preservation/reference review/build | No Python layer |
| T14 | Continuous results prose | Heading/content review/build | No Python layer |
| T12 | Integrated final layout | Rendered PDF/source reconciliation | No deferred software tests |

Software boundaries follow the existing components; related contract and
test files form one verifiable deliverable rather than an untestable
file-per-task split. No new architecture or test-type matrix is invented:
unit and cross-boundary integration requirements follow
`specs/codebase/TESTING.md`. Its historical test counts are not a baseline.

## T7 execution record — 2026-10-26

The author authorized T7 and confirmed filesystem/shell tools, CodeNavi and
sequential TLC delegation. T7.1 and T7.2 were already committed as
`81b633b` and `661f791`; their recorded regression proof was reviewed.
T7.3 completed as `acd458d`; T7.4 completed as `3d3d3ce`. T7.5 and task
tracking are recorded with the manuscript commit. Initial staging approval
was aborted; the author subsequently authorized another commit attempt.

- Software: format/lint/typecheck pass; final `uv run task test` reports
  327 passed, no failures or skips. Targeted T7.3 suite: 45 passed.
- Publication: fresh v3 package, ten sources, 204,300 observations, 609 output
  hashes checked; 3,743 raw-input/historical hashes unchanged. No mixed
  evidence versions. Review remains unresolved.
- Document: 11 referenced v3 assets match package bytes; `just build` passes
  (80 pages), no missing assets or unresolved references/citations. Affected
  prose and referenced asset pages were rendered and inspected.
- READ-07 is verified. Other tasks remain unchecked and outside this scope.
  Existing figure/table presentation issues remain assigned to T10–T12.
- Detailed counts, source-to-claim reconciliation, retained sigma caller
  classification and rendered-page locations are recorded in
  `docs/research/thesis_sigma_correction_validation.md`.

## T6, T9, T2 and T8 execution record — 2026-10-28

The author authorized the next four tasks with sub-agents. Four distinct
sub-agents executed T6 → T9 → T2 → T8 sequentially with local tools; no
additional tool approval was needed under that authorization.

- READ-01–READ-09 are now verified. Next task: T10.1.
- T9 localized numeric presentation in its owning generators and published
  v4 from existing v3 scientific evidence without rerunning experiments.
  The five generated presentation tables changed; scientific CSVs, figures,
  raw inputs and historical packages did not. All 609 v4 output hashes and
  4,353 preserved input/historical hashes pass verification.
- Current manuscript references eleven matching v4 assets exclusively.
  Pending task descriptions naming v3 tables refer to their corresponding
  current v4 presentation assets; historical completion evidence stays intact.
- Fresh software gates pass: format, lint, typecheck (zero errors/warnings),
  328 tests. Final document: 80 pages, resolved references/citations,
  affected pages rendered and inspected. Full-document integration remains
  T12; figure and detailed-table work remains T10/T11.
- Detailed source reconciliation, page inspections and task-specific proof:
  `docs/research/thesis_readability_validation.md`.
- Pre-existing edits in `TODOS.md` and staged planning changes in this file
  were preserved. This execution's task-status updates remain unstaged to
  avoid including the author's previously staged planning in task commits.

## T10.1–T10.4 execution record — 2026-10-28

The author authorized the next four tasks using sub-agents. Four distinct
agents executed T10.1 → T10.2 → T10.3 → T10.4 sequentially with local tools.

- READ-10 is verified. Next task: T11.1.
- The methodology now contains the authoritative workflow; conceptual and
  electrical-model illustrations retain their assets and distinct purposes.
- Presentation-only v5, v6 and v7 respectively coordinate distribution,
  geometric-index and sample-size figures from saved evidence, without
  rerunning experiments. Final v7 verifies 609 output hashes, ten raw-source
  hashes and 4,114 unique historical manifest-referenced paths. All 290 CSVs
  retain bytes, schemas and rows; eleven copied manuscript assets match v7.
- Final software gates pass: format, lint, typecheck (zero errors/warnings),
  333 tests. Final document: 83 pages, resolved references/citations, affected
  pages rendered and inspected. Whole-document integration remains T12.
- Task-specific acceptance, replay commands and rendered-page evidence:
  `docs/research/thesis_figure_coherence_validation.md`.
- Pre-existing TODOS.md and staged planning changes in this file remain
  preserved. Task-status updates remain unstaged, avoiding inclusion of
  previously staged planning in task commits.

## T11.1–T11.4 execution record — 2026-10-28

The author authorized the next four tasks using sub-agents. Four distinct
agents executed T11.1 → T11.2 → T11.3 → T11.4 sequentially with local tools.

- READ-11 is verified. Next task: T13, followed by T14 and T12.
- All four detailed tables appear exactly once in appendix sections; their
  former results locations contain connected summaries and automatic table
  and appendix references. Probability and sample-size evidence is preserved.
- Benchmark rows distinguish contamination from intensity and declare their
  evaluated group/scenario aggregation. All twenty conditions fit one
  landscape page. Five selected cases remain causally unresolved, with explicit
  controls and scenario/sample-size/full-path/hash source mapping.
- Presentation-only v8 and v9 reuse saved experiments. Final v9 verifies 609
  output hashes; 5,332 unique v1–v9 manifest-referenced paths, including ten raw
  inputs, pass verification. All 290 CSVs remain unchanged from v8 to v9;
  eleven copied manuscript assets match v9. No experiments were rerun.
- Final software gates pass: format, lint, typecheck and 342 tests. The final
  manuscript builds to 84 pages with resolved references/citations; affected
  prose and appendix pages were rendered and inspected. Whole-document
  integration remains T12.
- Task-specific reconciliation, regression proof, rendered pages and replay
  commands: `docs/research/thesis_table_relocation_validation.md`.
- Pre-existing changes in TODOS.md, spec.md, tasks.md and STATE.md were
  preserved. Tracking updates remain unstaged, separate from task commits.


## T13, T14 and T12 execution record — 2026-10-28

The author authorized the remaining queue with sub-agents. Three distinct
agents executed T13 → T14 → T12 sequentially with local tools.

- T13 merges the final discussion under the exact requested title, preserving
  four label aliases, numerical evidence and unresolved causal limitations.
- T14 removes five results subsections, retaining eight analytical sections
  and connecting extraction, probability, clustering and sample comparison.
- T12 verifies READ-01–READ-12 and TODOS REQ-01–REQ-05 against source and
  rendered pages. Six short list captions preserve full scientific captions;
  local single spacing retains table fonts and all rows while reducing each
  detailed probability/sample-size table from four to three landscape pages.
- Final manuscript: 81 pages, resolved references/citations, all-page overview
  and full-size review of every figure/table and table continuation.
- Publication-only replay into a new temporary directory reproduces all 609
  artifacts exactly, including 290 CSVs and 2,049,419 data rows. All 5,332
  unique v1–v9 manifest paths and eleven copied manuscript assets verify.
  No experiment, raw input, saved result or template asset changed.
- Software: 342 tests pass; scoped Ruff format/lint and typecheck on all 76
  tracked Python files pass. Broad Taskipy format/lint/typecheck commands
  traverse the unrelated untracked nested rip_atpdraw repository and fail
  there. Formatter changes in that repository were proved and restored;
  its working tree is clean. No unrelated code was changed.
- Detailed page inventory, preservation checks, gate scope and requirement
  reconciliation: docs/research/thesis_final_integration_validation.md.
- Pre-existing TODOS.md and planning/state changes remain preserved. Tracking
  updates remain unstaged, separate from the atomic implementation commits.
