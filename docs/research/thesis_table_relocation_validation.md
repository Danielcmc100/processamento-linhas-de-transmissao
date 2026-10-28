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
