# Thesis Readability and Sigma Correction Specification

**Status:** Partially implemented — READ-01, READ-03, READ-04, READ-05
and READ-07 verified; remaining requirements planned
**Created:** 2026-10-26
**Tasks:** [tasks.md](tasks.md)
**Scope:** Nine original editorial proposals, including the correction of the
three-sigma interpretation, plus figure, table, and final-layout review.
**Visual review:** `docs/research/thesis_visual_editorial_review.md`

## Problem statement

The thesis repeats scope limitations and software-audit details across
chapters, obscuring the scientific argument. Long paragraphs, inconsistent
terminology, and repeated objective-by-objective conclusions slow reading.
More importantly, the voltage three-sigma detector originated from a mistaken
interpretation of the statistical switch configuration.

## Author decision

The author clarified that three sigma belongs to the statistical circuit
breaker used in the ATP model, not to an anomaly criterion for output voltage.
Remove the output-voltage detector and its claims rather than qualify or
replace it. Do not change ATP switching settings or infer additional details
about their distribution without checking the source model.

This specification supersedes earlier requirements prescribing voltage
three-sigma screening, including the corresponding assumptions in existing
feature specifications and project guidance. Historical records remain
historical evidence, not current requirements.

## Goals and user stories

- **P1 — Correct analysis:** As the author, I want the active analysis and
  manuscript to exclude the mistaken detector, so the reported methods match
  the intended experiment. Independently verify through regression tests,
  regenerated evidence, and a classified search of sigma references.
- **P1 — Readable argument:** As a thesis reader, I want findings, methods,
  and limitations to have clear ownership, so I can follow the contribution
  without repeatedly reading audit details. Independently verify through an
  editorial comparison and a compiled document review.
- **P2 — Consistent presentation:** As a reader, I want defined terms,
  consistent tense, and readable tables, so terminology and formatting do not
  distract from the argument. Independently verify by glossary, tense, and
  table checks.

## Requirements and acceptance criteria

| ID | Proposal | Acceptance criteria |
| --- | --- | --- |
| READ-01 | 1. Consolidate limitations | WHEN reading scope and limitations, THEN the reader SHALL find the complete causal boundary there; elsewhere, only locally necessary caveats SHALL remain. A section inventory SHALL justify retained repetitions. |
| READ-02 | 2. Lead results with findings | WHEN opening the results chapter, THEN the reader SHALL encounter a short synthesis of validated data, exceedance, normality, and clustering applicability before audit details. Values SHALL match regenerated evidence. |
| READ-03 | 3. Relocate audit details | WHEN checking technical reproduction, THEN commands, full paths, line references, hashes, dates, and correction history SHALL be available in the appendix or linked research records. Main text SHALL retain methods, acceptance criteria, tolerances, outcomes, and essential electrical justification. |
| READ-04 | 4. Give paragraphs one purpose | WHEN reading the theory chapter, THEN definitions, literature, limitations, and application SHALL be separated into coherent paragraphs without changing citations or scientific meaning. |
| READ-05 | 5. Standardize terminology | WHEN encountering central terms, THEN computational routine, grouping, candidates, source identity, and applicability SHALL be used consistently; SRPI, CRPI, P.U., MAD, and AIC SHALL be defined at first substantive use and listed as appropriate. Portuguese spelling SHALL use centroide/centroides. |
| READ-06 | 6. Align verb tense | WHEN describing completed procedures, THEN the manuscript SHALL use past tense; concepts SHALL use present tense and genuinely pending work SHALL retain future tense. |
| READ-07 | 7. Correct methods and interpretation | WHEN running the active analysis, THEN voltage three-sigma thresholds, flags, votes, reasons, and detector overlays SHALL no longer be produced or required. The manuscript SHALL remove objectives, theory, comparisons, and conclusions that prescribe that detector. Switch settings SHALL remain intact. |
| READ-08 | 8. Shorten the conclusion | WHEN reading the conclusion, THEN contribution, principal findings, limitations, and future work SHALL appear as four concise blocks, without seven repeated declarations that objectives were met. |
| READ-09 | 9. Improve numeric presentation | WHEN reading prose and tables, THEN decimal/grouping conventions SHALL be consistent, precision SHALL suit interpretation, detailed tables SHALL be relocated only when summary coverage is preserved, and duplicate full paths SHALL be avoided. Machine-readable values SHALL retain computational precision. |
| READ-10 | 10. Improve figure coherence | WHEN reading a figure, THEN its caption SHALL describe what is actually plotted, identify its scope, and distinguish conceptual examples from 1D voltage results. Matching scenario panels SHALL use comparable scales, legible labels and explicit non-applicability. |
| READ-11 | 11. Increase table information value | WHEN reading result tables, THEN every row SHALL have sufficient experimental identity and informative differences. Identical results MAY be summarized only after verifying equality and retaining detailed evidence. Benchmark contamination and review-source identity SHALL be explicit. |
| READ-12 | 12. Verify final placement | WHEN reading the compiled manuscript, THEN figures/tables SHALL remain near the relevant discussion, without split referring paragraphs, clipping, unreadable text, or unnecessary landscape fragments. Validation SHALL include rendered-page review, not only compilation. |

### READ-07 invariants

1. The remaining candidate criteria are MAD, K-Means distance, and DBSCAN
   noise, subject to their existing applicability rules. Hierarchical labels
   remain descriptive and do not acquire a vote.
2. Candidate union, agreement, disagreement, applicable-method denominators,
   reasons, convergence summaries, and review selection must be recomputed.
   Do not assume previous candidate counts remain unchanged.
3. Preserve descriptive mean and sample standard deviation, Gaussian
   adequacy diagnostics, empirical exceedance, Wilson intervals, and the
   separately qualified Gaussian comparison. Removing a mistaken detector
   does not justify removing normality analysis or changing MAD's formula.
4. Classify generic sigma helpers and visual markers by actual callers.
   Remove helpers that become unused and output-voltage sigma screening
   presentations; retain independently justified functionality only with a
   documented caller and no anomaly-screening role. Do not add a replacement
   voltage-sigma detector or a compatibility flag to enable the old one.
5. Preserve raw ATP/LIS inputs and their switching-time parameters. A
   legitimate model description may mention three sigma with source support;
   a global textual deletion of the word sigma is forbidden.
6. State that narrower zero-event Wilson intervals reflect reduced
   uncertainty under the model, not independently established convergence.
   Prefer comparison across sample sizes where convergence is unproven.
7. Do not assert that skewness or kurtosis causally explains MAD behavior
   without a dedicated analysis. Describe their association cautiously.
8. Update active guidance to prevent reintroducing the mistaken detector;
   annotate superseded historical plans instead of rewriting their evidence.

## Implementation approach and repository grounding

Use the existing `specs/` layout, not a second `.specs/` tree. No new service,
external dependency, architecture document, or alternative detector is needed.

The pre-correction path was `pipeline.py:_add_sigma_evidence()` →
`comparison.py:compare_anomaly_methods()` → convergence and defense reports.
`statistics.py:summarize_statistics()` separately exported
`sigma_3_threshold`, and `schemas.py` declared its output contract.
`visualization.py` also drew voltage-sigma reference lines. T7.1–T7.3
removed those contracts with co-located tests; these pointers document
the baseline, not current APIs.

Generate a new evidence version, proposed as
`results/defense-evidence/v3/`, rather than overwrite v1/v2.
Before T7.3, `scripts/prepare_defense_document.py` hardcoded v2 and its
reference pattern. Publication routing now resolves versioned manuscript
references; T7.5 publishes v3 assets and keeps `doc/` independently compilable.

## Non-goals and preservation rules

- The original planning deliverable did not authorize implementation. The
  author subsequently authorized T7.1–T7.5 and confirmed local tools and
  sequential delegation. On 2026-10-27, the author authorized the next four
  tasks in canonical order (T1, T3, T4, T5), each in a distinct sub-agent;
  remaining tasks are outside this execution scope.
- Do not execute new ATP simulations, alter raw model inputs, or claim
  independent electrical review.
- Do not add causal labels, automatic deletion of extremes, insulation
  recommendations, distributions, or detection algorithms.
- Preserve citations, bibliography keys, electrical bases, observation
  identity, template assets, and existing numerical precision in raw data.
- Do not silently overwrite historical evidence or relabel old outputs as
  regenerated. If regeneration is blocked, report the blocker and do not
  publish mixed old/new evidence.
- Documentation is English; authored prose and comments in `doc/main.tex`
  must be Brazilian Portuguese. Any new reader-facing appendix prose should
  also be Brazilian Portuguese.

## Figure and table acceptance details

- Figure 1 must reflect `.lis` input, not claim an implemented `.OUT` parser.
  Keep provenance diagrams distinct from illustrative literature examples.
- Figures 9–10 retain both histogram and Q–Q evidence; remove mixed-language
  status and duplicated internal metadata. A distant 2.3 P.U. threshold must
  not obscure the observed distribution.
- Figures 11–12 must distinguish one terminal/phase from the nine-group
  median table and distinguish no eligible score from a score of zero.
- Figures 13–14 must not claim descriptive measures absent from the plots or
  label an across-N comparison as a single n=10000 dataset. Prefer panels
  using already computed descriptive statistics, rates and Wilson intervals.
- Probability compression may use five N rows only while all 18 groups per
  N agree. Preserve per-group denominators; never pool them as independent.
- The reference-group sample-size table must not imply full terminal/phase
  coverage. Keep exceptions and full detail traceable outside the main table.
- Benchmark tables must distinguish contamination percentage from intensity
  and state any aggregation scope. Review tables must distinguish sources
  sharing the `case.lis` basename and explicitly mark non-signaled controls.
- Preserve all original assets, even when an illustration is removed from
  the narrative. Generated plot/table changes belong to their generator.

## Verification strategy

Capture a current test baseline before implementation; the historical counts
in `specs/codebase/TESTING.md` are not current execution evidence. Explain
removed detector-specific tests and add regression coverage for the new
three-method contract. Preserve unrelated test coverage.

Software gate: `uv run task format`, then `uv run task lint`,
`uv run task test`, and `uv run task typecheck`.
Document gate: `just build`, no missing assets or unresolved citations or
references, plus visual review of tables, page breaks, and moved content.
Every retained sigma reference must be classified as switching configuration,
independently justified statistics, or explicitly historical evidence.

## Traceability and completion

READ-01 through READ-09 map to T1 through T9. T7 is decomposed into
T7.1–T7.5 because it crosses software contracts, publication, and manuscript
interpretation. READ-10 maps to T10.1–T10.4; READ-11 maps to T11.1–T11.4
and T9 for conversion/clustering presentation; READ-12 maps to T12.
READ-07 is implemented and verified through T7.1–T7.5. Evidence v3 was
regenerated from ten unchanged sources, all 609 output hashes were checked,
327 tests passed, and the 80-page manuscript compiled with affected-page
visual review. Detailed reconciliation and sigma-reference classification:
`docs/research/thesis_sigma_correction_validation.md`.
READ-01, READ-03, READ-04 and READ-05 are implemented and verified through
T1, T3, T4 and T5 in canonical order, each by a distinct sequential agent.
The current manuscript builds to 80 pages; preservation checks and affected
rendered-page review are recorded in
`docs/research/thesis_readability_validation.md`. T2, T6 and T8–T12 remain
planned; final whole-document layout acceptance belongs to T12.
T7.1–T7.4 have atomic commits, most recently `3d3d3ce`; T7.5 and task
tracking are recorded with the manuscript commit after the author authorized
retrying the interrupted staging operation. The generated `results/` package is
Git-ignored; referenced v3 manuscript assets are present in `doc/evidence/`.
