# Contribution of upper-tail clustering to the manuscript

Analysis date: 2026-10-05.
Sources: `doc/main.tex`, `src/services/clustering.py`,
`src/services/pipeline.py`, `src/services/comparison.py`, and the regenerated
case outputs analyzed in `doc/hierarchical-regenerated-results-analysis.md`.
The manuscript was not changed by this analysis.

## Main contribution

The new rule provides an explicit way to distinguish a locally isolated
upper maximum from a densely populated high-voltage region. This directly
supports the justification in `main.tex` concerning the limits of using
the single largest ATP value as the only analytical reference. Its output
prioritizes runs for investigation while retaining every observation.
It does not replace the ATP extrema calculation, reconstruct waveforms,
estimate numerical error, validate Gaussianity, or justify discarding a
maximum from insulation studies.

The strongest defensible claim is that the implementation automates a
previously visual selection through a reproducible terminal-local gap
criterion. Matching the marked 50-shot example demonstrates requested
behavior, not superiority over other detectors: parameter choices were
informed by that example, which is not an independent evaluation dataset.

## Relationship to existing manuscript sections

| Manuscript anchor | Contribution | Needed qualification |
| --- | --- | --- |
| General and specific objectives, lines 473–496 | Adds an unsupervised grouping approach to locate separated upper observations | Existing examples K-Means and DBSCAN need not be replaced; describe the extension explicitly |
| Scope, lines 520–524 | Preserves traceability and supports subsequent technical investigation | Avoid calling label zero physically normal or label one an ATP error |
| Peak normalization, lines 1028–1039 | Reuses signed per-run maxima normalized through absolute magnitude | Distinguish per-run observations from the ATP summary `Peak extremum of subset` |
| Contextual evidence, lines 1186–1219 | Complements centroid distance and density noise with upper-tail separation | Current fit is terminal-local only, unscaled, and uses the complete analyzed sample |
| Anomaly results, lines 1531–1563 | Adds a separately reported exploratory grouping result | The existing four-method consensus and its counts are unchanged |
| Controlled evaluation, lines 1623–1656 | Provides another method that could later enter the evaluation protocol | Existing benchmark metrics and Jaccard results cover K-Means/DBSCAN, not this rule |
| Discussion and limits, lines 1672–1757 | Shows that absolute voltage and local isolation are different properties | Sample-size changes and parameter sensitivity do not prove error rate or convergence |
| Conclusion, from line 1760 | Supports reproducible organization of candidates for technical review | No claim of validated causal detection or improved insulation design follows |

Line numbers are navigation anchors in the inspected manuscript version.

## Method that should be documented

For each terminal, sort N voltage maxima as x(1) <= ... <= x(N), and define
adjacent spacings g(i) = x(i+1) - x(i). In one dimension these gaps are
single-linkage merge distances. The implementation evaluates eligible
upper-tail boundaries and selects the largest gap satisfying:

- i >= 3 reference observations;
- (N - i) / N <= 0.10;
- g(i) > max(0.05 P.U., 5 * median(g)).

Observations above that boundary receive label one; all others receive
zero. No qualifying boundary yields an undivided reference group.
Median spacing includes repeated values with zero gaps. The defaults are
exploratory settings, not electrical safety limits or a statistical
significance level. Explain this as a single-linkage-inspired upper-tail
selection rule rather than implying a general complete-linkage clustering
analysis or automatic discovery of every operating regime.

The algorithm does not establish that reference observations form a
uniformly dense or physically normal population. It only establishes that
the selected upper subset satisfies the declared boundary criterion.

Patito input/output validation contributes to software reliability through
required-column, type, nullability, and binary-label checks. It does not
provide electrical or statistical validation. Original observation identity
and row order remain available for locating the source simulation.

## Results eligible for inclusion now

The five regenerated CSVs contain only SRPI, phase A, at three terminals:
3 * (50 + 100 + 200 + 1,000 + 10,000) = 34,050 scalar observations.
This is an exploratory subset of the 204,300-observation SRPI/CRPI,
three-phase scope described in the manuscript. Do not attribute coverage
of all 90 groups to the hierarchical analysis.

| Shots | T_MAN selected | Midpoint selected | T_OPO selected |
| ---: | ---: | ---: | ---: |
| 50 | 1 | 3 | 0 |
| 100 | 0 | 0 | 0 |
| 200 | 3 | 0 | 0 |
| 1,000 | 0 | 1 | 0 |
| 10,000 | 0 | 1 | 0 |

The 50-shot example is useful to explain the criterion: the selected
T_MAN maximum is 1.651738 P.U., separated by 0.133009 P.U.; the three
midpoint maxima are 2.008931–2.039735 P.U., separated by 0.078676 P.U.
The dense upper T_OPO band remains unselected. The 100-shot result
illustrates that the method allows no separated tail.

Parameter sensitivity should accompany the table. Raising the gap factor
to 5.5 removes the 50-shot midpoint selection. Raising the absolute floor
to 0.06 P.U. removes the 200-shot T_MAN selection. The isolated midpoint
maxima at 1,000 and 10,000 shots persist under the tested small changes.
These measurements provide local sensitivity evidence, not independent
detection accuracy or resampling stability.

## Integration boundaries

`compare_anomaly_methods()` reads sigma, MAD, K-Means distance, and DBSCAN
flags only. Hierarchical labels never vote. In particular, the three
selected midpoint observations at 50 shots remain
`anomaly_candidate=false`. Present that as an explicit difference between
descriptive selection and the current candidate-generation policy.

The contextual grouping described for K-Means and DBSCAN in the manuscript
includes scenario, lineage, terminal, and phase; the hierarchical function
currently groups only by terminal. This suffices for the inspected
single-scenario, single-phase case outputs, but cannot be extended to a
combined three-phase SRPI/CRPI population without a declared grouping
policy and verification against that policy.

The existing `hierarchical_tree.png` is a global Ward dendrogram. It is
not a diagnostic tree for the implemented terminal-local single-linkage
rule and should not be presented as its methodological justification.
Use the regenerated scatter and a table of gaps/thresholds instead.

## Recommended manuscript integration

1. Add a short theoretical subsection on single linkage and its connection
   to sorted one-dimensional spacings, with an appropriate bibliography
   source verified before inserting it.
2. Add a separate exploratory-method subsection adjacent to contextual
   K-Means/DBSCAN evidence. Declare input maxima, grouping, parameters,
   binary-label meaning, and exclusion from consensus.
3. Add a results subsection before or after anomaly evidence, explicitly
   limited to the 34,050-observation SRPI/phase-A subset. Include the count
   table, representative 50-shot scatter, and sensitivity findings.
4. Extend discussion and conclusion with the demonstrated contribution:
   reproducible selection of locally separated upper groups. Retain the
   existing unresolved-cause and no-automatic-discard restrictions.

If the method becomes a central detector rather than a complementary
exploratory visualization, further work is necessary: contextual grouping,
complete matrix coverage, recorded parameter/threshold provenance,
independent controlled evaluation, and quantified selection stability.
Existing K-Means/DBSCAN performance claims cannot be transferred to it.
All prose subsequently inserted into `doc/main.tex` must be Brazilian
Portuguese, as required by the project instructions.
