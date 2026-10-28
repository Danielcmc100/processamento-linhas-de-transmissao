# Detailed Table Relocation Validation

## T11.1 — Probability table (2026-10-28)

Scope: editorial relocation using the existing v7 package. No experiment,
Python code, raw input or generated asset changed. Pre-existing edits in
TODOS.md and specification/project tracking files remain untouched.

### Source reconciliation

All 90 rows of `doc/evidence/v7/tables/probability.tex` were matched by
scenario, sample size, terminal and phase to full-precision
`results/defense-evidence/v7/sources/convergence.csv`. All keys are unique;
each denominator equals its group sample size; all event counts, empirical
probabilities and Wilson lower bounds are zero; all statuses remain valid.
Summing group observation counts gives 204,300 scalar observations. This
describes coverage, not a pooled probability estimator.

All 18 groups at each N share these Wilson 95% upper bounds:

| N | Full-precision upper bound |
| --- | --- |
| 50 | 0.07134759913335872 |
| 100 | 0.03699349820698568 |
| 200 | 0.018845326377266575 |
| 1,000 | 0.0038267584855551234 |
| 10,000 | 0.00038399837067659573 |

Every displayed upper bound matches its source within half the last
displayed decimal place (0.00005). No exception was omitted. Main prose
retains endpoints 0.0713 and 0.0004, zero observations above 2.3 P.U. in
all 90 groups, per-group denominators and explicit uncertainty about the
underlying probability. The 1,151 ATP interval comparisons and Gaussian
adequacy findings remain unchanged.

### Relocation and editorial gate

The probability table input occurs exactly once in `doc/main.tex`, after
the appendix environment starts, under the titled section
`app:probabilidades-detalhadas`. Its former inclusion now contains
connected Brazilian Portuguese prose with automatic references to both
`tab:defesa-probabilidade` and the appendix destination. Package provenance
still references `app:pacote-evidencias`. No main-text replacement table.
All 90 rows, caption, label and generated source bytes remain unchanged;
table SHA-256: `95d1047166b368280eae9f51b90bc4e94be8049ee298e151c76a410a4a21596d`.

`just build` passes: 83 PDF pages. Final LaTeX log has no undefined
references/citations, duplicate labels, missing assets or overfull boxes.
At this snapshot the table is numbered 7 and appendix section A.6; these
numbers are evidence only, never hard-coded manuscript references.

Rendered using `pdftoppm`, then visually inspected:

- PDF pages 49–50 (printed 48–49): prose flows into Gaussian adequacy;
  references resolve to Table 7 / Appendix A.6 / Appendix A.5.
- PDF page 79 (printed 78): titled appendix destination and provenance.
- PDF pages 80–83 (printed 79–82): four landscape table pages, repeated
  headers, complete first/last rows, no clipping or overlap. The existing
  final continuation has seven rows. Whole-document whitespace integration
  remains T12; table layout was preserved.

Transient previews: `/tmp/t11-1-pages/`. Reproduce with
`pdftoppm -f 49 -l 50 -png doc/build/main.pdf /tmp/t11-prose` and
`pdftoppm -f 79 -l 83 -png doc/build/main.pdf /tmp/t11-appendix`.

### Verification gates

`uv run task format` and `uv run task lint` pass; formatting leaves all
174 files unchanged. `uv run task test` passes: 333 tests, no failures or
skips. No software changed, so no additional software/publication gate applies.
Publication gate is unnecessary because generated content did not change.
No specification deviation. Whole-document integration remains T12.

## T11.2 — Sample-size table (2026-10-28)

Scope: editorial relocation of the existing v7 comparison table. Only
`doc/main.tex` and this report changed; no Python, experiment, source CSV,
generated asset, template or pre-existing planning edit changed.

### Source reconciliation

All 90 table rows have unique scenario/N/terminal/phase keys and match
`results/defense-evidence/v7/sources/convergence.csv`. The 450 displayed
mean, percentile-95, empirical-probability, interval-width and candidate-rate
values agree within half their last decimal place (0.00005); all candidate
counts match exactly. Thousands separators were normalized for N and counts.
All rows share base 112677 V, threshold 2.3 P.U., strict `>` comparison,
`scenario|source_lineage|terminal|phase` grouping and
`defense-v3-three-methods` policy. All 90 comparison states are comparable;
independence remains unestablished.

Each of the 18 scenario/terminal/phase sequences covers N = 50, 100, 200,
1,000 and 10,000. Its zero-event Wilson width decreases strictly through
the five full-precision values recorded for T11.1 above. The prose retains
the interpretation as reduced uncertainty under the interval model, without
claiming independently proven convergence or accuracy.

Restricted T_OPO/phase-A candidate examples reconcile as follows:

| Scenario | N=50 | N=100 | N=200 | N=1,000 | N=10,000 |
| --- | --- | --- | --- | --- | --- |
| CRPI candidate count | 8 | 12 | 2 | 10 | 109 |
| CRPI candidate rate | 0.16 | 0.12 | 0.01 | 0.01 | 0.0109 |
| SRPI candidate count | 6 | 12 | 22 | 86 | 852 |
| SRPI candidate rate | 0.12 | 0.12 | 0.11 | 0.086 | 0.0852 |

CRPI's five rates are explicit in the prose; SRPI's retained 8.52%–12%
range matches all five records. Figures 13–14 display these same values,
the corresponding means/percentiles and the zero-event Wilson intervals.
The prose explicitly restricts examples to T_OPO/phase A, treats N=10,000
as an empirical reference rather than truth, and does not presume source
independence or nesting. Other terminal/phase coverage remains in the full
table, with no replacement main-text table.

### Relocation and editorial gate

The table input occurs exactly once, inside the appendix environment under
`app:comparacao-amostral-detalhada`, with its original caption,
`tab:defesa-convergencia`, 90 rows and provenance preserved. Main prose
references both table and appendix section automatically. Generated table
SHA-256 remains
`ab646ae13f7382783ee4df9a8b3a1b685b0f7403c9deebea2f27b2c7b72517d1`.

`just build` passes: 84 PDF pages, without undefined references/citations,
duplicate labels, missing assets or overfull boxes in the final log.
Rendered with `pdftoppm` and visually inspected:

- PDF page 57 (printed 56): complete connected comparison prose, automatic
  Table 7 / Appendix A.7 references and explicit limited figure scope.
- PDF pages 58–59 (printed 57–58): unchanged Figures 13–14 agree with the
  numeric prose and retain readable uncertainty and scope annotations.
- PDF page 80 (printed 79): appendix A.7 title and provenance introduction.
- PDF pages 81–84 (printed 80–83): all four landscape continuations,
  repeated headers, first/last rows, no clipping or overlap. The last page
  retains nine rows. Final whole-document whitespace integration remains T12.

Transient previews: `/tmp/t11-2-pages/`. Replay rendering with
`pdftoppm -f 57 -l 59 -scale-to 1250 -png doc/build/main.pdf
/tmp/t11-2-prose` and the corresponding `-f 80 -l 84` appendix range.

### Verification gates

`uv run task format` and `uv run task lint` pass; formatting leaves all
175 files unchanged. `uv run task test` passes: 333 tests in 95.54 seconds,
with no failures or skips.
No software/publication gate is required for unchanged generated content.
No specification deviation. Whole-document integration remains T12.


## T11.3 — Identifiable controlled benchmark (2026-10-28)

### Implementation and source reconciliation

- Relocated the full benchmark exactly once to appendix section
  `app:benchmark-detalhado`; retained caption and `tab:defesa-benchmark`.
  Main-text prose references both labels and retains clean-baseline false
  positives, family-specific recall/F1 tradeoffs, tested contamination rates,
  restricted reference-group scope, and the synthetic/causal boundary.
- The generator now requires and displays requested/effective contamination
  percentages separately from perturbation intensity and evaluation count.
  Row keys include both rates and evaluation count: all 20 saved conditions
  have unique traceability keys. Intervention families use Portuguese labels.
  DBSCAN's density-novelty meaning is shared in the appendix scope statement.
- Compared every rendered confusion count and metric against saved full-
  precision `v7/tables/benchmark.csv`: all 20 rows and 160 cells agree after
  four-place presentation rounding, including undefined clean-baseline recall.
  Requested/effective rates are 0% for the clean baseline and 1%, 5%, 10%
  for each intervention family/method, at fixed family-specific intensities.
- Shared scope explicitly identifies aggregation over CRPI and SRPI,
  T_OPO/phase A, sources with 10,000 simulations, and 5,400 evaluation
  observations per row. No other terminal/phase or causal accuracy is implied.

### Regression and software gates

- RED: the new fixed-intensity/three-contamination regression failed because
  the prior formatter emitted one unique key instead of three.
- GREEN: ten reporting tests pass; the regression asserts percentages,
  translated intervention, all confusion counts/metrics, unique trace keys,
  and unchanged scientific values in generated CSVs.
- `uv run task format`, `uv run task lint`, and `uv run task typecheck`
  pass; typecheck reports zero errors, warnings or notes.
- Fresh `uv run task test`: 334 passed in 98.16 seconds, no failures/skips.

### Publication and document gates

- `uv run python -m docs.research.replay_thesis_benchmark_table` creates v8
  from immutable v7 saved evidence, without running experiments. Only
  `tables/benchmark.tex` and `tables/table_traceability.csv` change.
  The manifest records inherited experiment provenance, replay command,
  implementation hashes and `experiments_rerun: false`.
- All 289 scientific CSVs retain bytes (the 290th CSV is presentation
  traceability, intentionally corrected). All v1–v8 manifests verify:
  4,723 unique referenced paths, including ten raw inputs; v8 has 609 output
  hashes. Historical packages and raw inputs remain unchanged.
- Eleven manuscript assets exclusively reference v8 and match package bytes.
  Preparation command: `uv run python -m scripts.prepare_defense_document`.
- `just build` passes: 84 PDF pages; final log has no undefined references,
  citations, duplicate labels, missing assets or overfull boxes.
- Rendered physical PDF pages 60, 83 and 84 inspected at final-size scale:
  main synthesis, appendix scope/provenance and full table. All twenty rows
  fit one landscape page (PDF 84, printed 83), with readable 10pt type,
  all detailed metric columns, intact caption and explicit percentages.
  No trailing-row landscape continuation remains. Source contains one
  benchmark inclusion, in the appendix only.
- Whole-document reflow remains T12; no T13/T14 work performed. No spec
  deviations. No new notebook entry: generator/replay ownership is recorded
  here and existing scope notes already cover the scientific boundary.


## T11.4 — Pending electrical-review cases and source identity (2026-10-28)

### Plan and acceptance reconciliation

- Assumption: immutable v8 retains the five selected cases and the authoritative
  dataset catalog. This task changes presentation only, with no experiments,
  electrical review, or causal conclusions added.
- Task-owned files: manuscript; defense-reporting generator and tests; builder
  catalog wiring; existing presentation replay callers; v9 manuscript assets;
  this evidence record. Pre-existing TODOS/spec/task/state edits are preserved.
- The detailed table is included exactly once, in the titled appendix section
  `app:casos-revisao-pendente`, retaining its original caption and
  `tab:defesa-revisao-tecnica` label. Main prose references both targets and
  reports five unresolved cases, missing waveforms/repetitions/qualified review,
  and pending electrical review rather than completed validation.
- Every observation retains simulation, terminal, phase, signed source value,
  P.U. value and analytical evidence. Shared conclusion, reviewer, date and
  rationale appear once in a note only when genuinely identical; differing
  per-case values remain separate columns.
- The control is explicitly identified as `controle sem sinalização`, including
  empty evidence read from CSV as null. No empty evidence cell remains.
- Four cases resolve to CRPI, N=100, and one to CRPI, N=1000. Both source
  identities display full repository-relative paths and full SHA-256 values.
  All five rows, ten voltage values, simulation/terminal/phase identities and
  method evidence were reconciled against saved full-precision review data and
  `sources/dataset_manifest.csv`. The map declares the repository root.

### Regression and software gates

- RED confirmed missing source-catalog support; duplicate-basename/blank-control
  and missing/ambiguous identity regressions failed before implementation.
  A separate basename-only catalog regression reproduced misleading publication,
  and a contextual traceability test reproduced duplicate keys for identical
  bytes assigned to different scenarios. Each subsequently passed.
- Eight new tests cover duplicate basenames, explicit empty/null controls,
  shared versus differing review status, missing/ambiguous/basename-only source
  identities, and identical-byte sources disambiguated by known scenario/N.
  Source validation runs before writing any artifact.
- The first full gate exposed an integration fixture with identical source bytes
  across several contexts. The builder now preserves known scenario/N in future
  review records; catalog lookup and trace keys use that context. Historical
  hash-only records require a unique catalog match. Saved CSVs remain unchanged.
- One new preservation-test CSV read was corrected with parent approval to
  `missing_utf8_is_empty_string=True`, matching source empty-string semantics
  rather than weakening the assertion. Test setup also fixes an Int32/Int64
  concatenation mismatch before GREEN.
- Reporting suite: 18 passed. Builder/reporting integration checkpoint: 22
  passed (collected before the last two unit tests were added).
- Final `uv run task format`, `uv run task lint`, and
  `uv run task typecheck` pass; typecheck has zero errors/warnings/notes.
  Final `uv run task test`: **342 passed in 86.52 seconds**, no skips/failures,
  up from the fresh preceding T11.3 baseline of 334 tests.

### Publication and rendered-document gates

- Replay command: `uv run python -m
  docs.research.replay_thesis_benchmark_table --source
  results/defense-evidence/v8 --output results/defense-evidence/v9 --table
  technical_review`. The existing replay owner now accepts benchmark/review
  selection and source/output directories; default benchmark replay is retained.
- Only `tables/technical_review.tex` changes between saved v8 and final v9.
  All **290 CSVs**, including presentation traceability, retain bytes, schemas,
  rows and scientific precision. No experimental routines run. The v9 manifest
  records inherited provenance, replay command, current implementation hashes
  and `experiments_rerun: false`.
- All **609 v9 output hashes** and all v1–v9 manifest-referenced paths verify:
  **5,332 unique paths**, including the ten raw inputs. Historical packages and
  raw sources remain unchanged. Current implementation hashes also reconcile.
- `uv run python -m scripts.prepare_defense_document` copies eleven referenced
  assets; every manuscript reference uses v9 and matches package bytes.
- `just build` passes: **84 PDF pages**. Final log contains no undefined
  references/citations, duplicate labels, missing assets or overfull/underfull
  boxes. Original table caption/label and appendix references resolve.
- Physical PDF pages **60–61, 83–84** were rendered and inspected: main prose
  and its continuation, appendix heading/provenance, and the complete table.
  All five cases and both full source maps fit one readable landscape page
  (PDF 84, printed 83); common notes and control are legible, without clipping.
  Original table numbering remains Table 7. Source contains one inclusion only,
  after the appendix begins.
- No T13/T14/T12 work performed. Whole-document integration remains T12;
  electrical review remains unresolved. No specification deviations. No new
  notebook entry: this record captures the catalog/replay ownership and the
  existing scope notebook already documents pending causal validation.
