# Thesis Figure and Table Editorial Review

**Date:** 2026-10-26
**Scope:** Read-only analysis of `doc/main.tex`, all 14 referenced figures,
all seven tables, their local assets, and `doc/build/main.pdf`.
**Related plan:** `specs/features/thesis-readability-and-sigma-correction/`.

## Evidence and limits

`just build` reported the PDF up to date. The inspected document has 81 PDF
pages. Page numbers below are physical PDF positions, not printed manuscript
numbers (these currently differ by one). Placement was checked through
rendered pages; table semantics were also checked against the LaTeX sources.
No manuscript, plot generator, table generator, or dataset was changed.

The existing float diagnosis in
`docs/research/latex_float_layout_diagnosis.md` remains relevant: successful
compilation does not guarantee desirable reading order. Global permissive
typesetting settings also make absence of log warnings insufficient proof of
readability.

## Overall assessment

The electrical-model figures and distribution diagnostics have a clear role.
The largest information-density problem is the presentation of exhaustive
evidence tables as main-text results. Probability and sample-size tables
each occupy four landscape pages, interrupting the argument. Some graphs
repeat table content without exposing variation or uncertainty clearly.

More serious than appearance are missing experimental identifiers in the
benchmark table, ambiguous source identifiers in the review table, and
captions claiming content absent from sample-size figures. Correct these
before reducing font sizes or adjusting floats.

## Figures: decisions and rationale

| Figure | Location | Assessment | Recommended treatment |
| --- | --- | --- | --- |
| 1 — General workflow | PDF 20 | The logical flow is useful, but labels are small at 75% text width. It labels ATP output as `.OUT`, while the implemented parser consumes `.lis`. It describes the project's procedure inside theoretical background. | Keep one workflow, preferably in methodology; correct the file-format label to the actual input and distinguish simulation generation from Python processing. Improve size/crop without changing model semantics. |
| 2 — Colqui line model | PDF 22 | Coherent as a literature example, but is not the studied network. Its role overlaps the actual-model diagrams. | Keep only if the text uses a specific feature of this example; otherwise remove its main-text inclusion or relocate it. Explicitly identify it as a literature example, not the 138 kV model. Preserve the original asset and citation. |
| 3 — Synthetic scatter diagram | PDF 24 | Legible and useful for a basic grouping concept, but two-dimensional imagery may suggest the actual detector uses two features. The active analysis is one-dimensional voltage. | Retain as a single clearly illustrative schematic and explicitly state that the experiment uses only voltage; do not treat the schematic as a result. Correct centroide spelling. |
| 4 — Twenty-cluster K-Means example | PDF 28 | Thin three-panel image with tiny labels. Appears at the start of a page continuing DBSCAN discussion. It adds another generic grouping illustration, not evidence about the actual k=2 experiment. | Prefer remove/relocate from the main narrative unless the text makes a distinct necessary comparison. Preserve asset/citation; if retained, keep it with K-Means discussion and readable labels. |
| 5 — SOM/K-Means/DBSCAN example | PDF 29 | Useful density-versus-centroid comparison, but low-resolution raster labels and a method not used in the experiment add cognitive load. Arbitrary 2D shapes do not establish performance in 1D voltage. | Retain only as a concise conceptual comparison with the 1D limitation explicit; avoid keeping all generic illustrations when they serve the same explanatory role. Never infer actual detector superiority from this figure. |
| 6 — ANAFAS equivalent | PDF 33 | Necessary provenance diagram. Together with Figure 7 it demonstrates conversion, rather than duplicating the same evidence. Small bus labels are hard to read. | Keep; crop unused canvas and emphasize buses/equivalents actually discussed. Use detailed supplementary view if full labels cannot be read at normal size. |
| 7 — ATPDraw network | PDF 34 | Necessary implementation diagram. The referring paragraph ends on this page with only “arquivos de saída.” above the figure. | Keep, improve labels/crop, and reflow so the referring paragraph is not split this way. Avoid blanket `[H]` placement. |
| 8 — Studied line | PDF 35 | Useful spatial explanation of the four sections and monitoring points. Wide diagram has small labels. | Keep; ensure 80 km segmentation, the three terminals, and phase measurements are legible. Do not redraw or change engineering values without source verification. |
| 9–10 — Distribution and Q–Q | PDF 53–54 | Strong evidence against normality; not redundant because scenarios have different shapes. Histograms include large empty ranges up to 2.3 P.U.; titles duplicate scope and mix Portuguese with “rejected”. | Preserve both diagnostics, preferably as coordinated scenario panels. Use comparable histogram bins/scales where comparing scenarios; show the distant threshold without compressing the observed distribution (annotation or separate view). Remove duplicated internal metadata headings and translate reader-facing status. |
| 11–12 — Clustering indices | PDF 58–59 | Match the geometric analysis, but scenarios use different y-axis ranges. In the selected terminal/phase, DBSCAN has no plotted valid score despite a legend entry. Figure 11's page leaves substantial unused space before Figure 12. | Coordinate scenarios in one comparison layout with the same range for each corresponding metric and consistent method styles. Explicitly show non-applicability rather than an apparently missing curve. Retain the distinction from the table's nine-group medians. |
| 13–14 — Sample-size comparison | PDF 65 | Actual curves show only empirical probability and candidate rate; captions additionally promise descriptive statistics. Wilson uncertainty is not drawn. The 0–1 y-range hides variation below 0.16. Titles mix languages and state n=10000 although the x-axis spans five sample sizes. | Correct captions and scope labels. Prefer coordinated panels for descriptive measures, candidate rate, and exceedance uncertainty using existing computed data; otherwise narrow the captions to actual content. Use shared, honestly labeled useful ranges for matching scenario panels; do not treat zero probability as certainty or fill missing values with zero. |

No blanket removal of paired CRPI/SRPI figures is justified: their differences
are substantive. Consolidation should enable comparison, not erase scenarios.
Any replacement diagram must retain source engineering values and preserve
template assets even when no longer referenced.

## Tables: information value and defects

### Table 1 — ATPDraw mapping (PDF 33)

Keep. Its six rows explain model provenance without duplicating the figures.
Column widths and concise phrases can improve readability. Keep it near its
introduction; it should not force an unrelated paragraph around another float.

### Table 2 — P.U. validation (PDF 46)

Keep a compact example. The paired columns with approximately 18 decimals
are difficult to compare and largely repeat the same values. Prefer an
interpretable converted value plus absolute error and acceptance tolerance.
If displayed values are rounded, compute the error from full-precision values,
not from their rounded display. Preserve detailed checkpoints in evidence.

### Table 3 — Exceedance probability (PDF 49–52)

This is the clearest case of low information density. All 90 rows have zero
events and zero empirical probability; denominator repeats N; status is always
valid. For fixed N, both interval bounds repeat across 18 scenario/terminal/
phase groups. In the current data, a five-row summary by N communicates the
result, with a note specifying that it applies separately to all 18 groups.

Do not pool the 18 groups or use 18N as the binomial denominator. Preserve the
90-group table in the appendix/evidence and recompute whether compression is
valid on every generation. If groups cease to have identical results, show
the exceptions explicitly or retain the grouped rows.

### Table 4 — Clustering comparison (PDF 56)

Keep as a main-text synthesis: 30 rows summarize 270 records and applicability
is meaningful information, not useless missing data. Repeated NA entries can
be shortened with separate applicability and score views or grouped blocks,
but must not disappear. Improve column grouping/order and explain A/9 and DB.
Do not directly equate these medians across nine groups with Figures 11–12,
which show only T_OPO phase A. Do not replace NA by zero or rank methods with
different retained populations as if they were evaluated identically.

### Table 5 — Sample-size comparison (PDF 61–64)

The table contains useful changes in mean, percentile 95, and candidates, but
four landscape pages obscure them. Probability zero and Wilson widths repeat
Table 3, and status is uniformly comparable. Retain a compact comparison for
the declared reference terminal/phase across both scenarios (ten rows),
with sample size, mean, percentile, candidate count and rate. Detailed
terminal/phase coverage remains available in the appendix or a concise
full-scope summary. Do not silently imply that the reference group represents
all phases or terminals. Give the uncertainty information one main owner.

### Table 6 — Controlled benchmark (PDF 67–68)

**Correctness priority:** The table displays intervention intensity but omits
contamination fraction. Consequently, three rows have the same intervention,
intensity and method, although they represent 1%, 5%, and 10% contamination.
Rows are not uniquely identifiable without reverse-engineering TP+FN counts.

Show contamination as a separate percentage column, distinct from magnitude
intensity. State scope and how scenario/group counts are combined; check the
source table before choosing a summary. Translate clean/point/contextual/
collective labels for the thesis. Keep precision, recall, F1 and false-positive
rate in a readable summary; move the full confusion counts to the appendix
if needed. The current table spills just two data rows onto the second
landscape page; redesign instead of further shrinking the font.

### Table 7 — Technical review (PDF 70)

All five rows repeat the same unresolved conclusion, unavailable reviewer,
unperformed date, and missing-evidence justification. Use a shared note for
these common limitations and a compact table for actual differences.

**Traceability priority:** Source is rendered as `case.lis` in every row,
although that basename is not globally unique. Display scenario, sample size,
and a source identifier mapping to the full relative path/hash in evidence.
Retain simulation, terminal, phase, voltage and analytical evidence. An empty
evidence cell should explicitly identify a non-signaled control, not leave
the reader to infer whether data are missing. Do not call the rows completed
electrical reviews: they are selected cases pending electrical review.

## Layout and publication rules

- Prefer a table or chart per analytical question; do not reproduce an entire
  CSV just because it exists.
- Keep first references close to the displayed object, with no intervening
  topic change; avoid isolated trailing lines such as PDF 34's opening.
- Reassess the explicit `\clearpage` before the clustering table after table
  redesign. Prefer deliberate local float control over blanket rigid floats.
- Use portrait layout for summaries when readable; reserve landscape for
  genuinely wide details, preferably in the appendix.
- Reader-facing plots should have Brazilian Portuguese labels, consistent
  units, legible text at final size, and matching scales for like comparisons.
- Captions identify scope and content; common validity disclaimers belong in
  notes/prose, not repeated in every internal plot title.
- Fix generated assets in `defense_reporting.py` or their plot owner and
  regenerate. Do not make manual edits that the next run will overwrite.
- Recheck all placements after sigma removal and shortened prose: current page
  positions are diagnostic evidence, not permanent layout requirements.

## Priority

1. Correct benchmark condition identity, review-source identity, and false
   sample-size captions.
2. Compress exhaustive probability/sample-size tables without pooling groups
   or dropping exceptional results.
3. Coordinate scenario charts and reveal useful variation/uncertainty.
4. Reduce redundant generic theory illustrations and improve model labels.
5. Reflow the final manuscript and inspect the complete compiled PDF.
