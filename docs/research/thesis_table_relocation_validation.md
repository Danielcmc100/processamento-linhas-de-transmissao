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
