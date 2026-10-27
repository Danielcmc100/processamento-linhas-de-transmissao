# Thesis readability validation

## T1 — Consolidated limitations (READ-01)

Executed on 2026-10-27 after verified T7.5. This editorial task changes
`doc/main.tex` only; data, software, generated evidence and template assets
are unchanged. The author's current four-task implementation request
authorizes local filesystem/shell tools and sequential TLC delegation.

### Section inventory and ownership

| Limit or boundary | Canonical owner | Retained local qualification and reason |
| --- | --- | --- |
| Candidate generation, no definitive physical/numerical/data-defect classification | `sec:escopo-limites`, section 1.4 | Abstract remains self-contained; methodological output names remain explicit. |
| No automatic removal, expert system or insulation recommendation | `sec:escopo-limites`, section 1.4 | Methodology preserves the operational rule that flags do not alter denominators; conclusion briefly links the scope and partner responsibility/IP. |
| Data/statistical/detector/electrical validity are separate | `sec:camadas-validade`, section 4.6.1 | Results opening and internal-index definition now refer to this owner instead of repeating the causal disclaimer. |
| Scalar maxima do not describe waveform duration, frequency, rate of change or oscillatory content | `sec:alcance-limitacoes`, section 5.11 | Normalization retains the narrower warning that sampled/printed maxima do not establish a continuous-time global maximum. |
| Missing waveforms, reduced-step repeat simulations and independent qualified electrical reviewer | `sec:lacunas-pacote`, section 5.11.1 | Technical-review results retain the five unresolved cases and refer to the complete explanation; conclusion refers to the same owner. |
| Incomplete package and unresolved causal conclusion, including all candidates | `sec:lacunas-pacote`, section 5.11.1 | Package-status evidence stays explicit; discussion retains experimental findings and points to the following limits. |
| Parser/structure acceptance covers declared layouts, printed precision and selected numerical checkpoints | Results sections 5.1–5.2 | Retained: whole-collection count reconciliation is not exhaustive numerical validation; phase-A checkpoint coverage is narrower than structural coverage; old CRPI exports require regeneration. |
| P.U. acceptance is conversion of printed phase-ground maxima | Results section 5.3 and `sec:per-unit-validation` | Retained: 112677 V versus 195161 V distinction, electrical derivation, tolerances, changed-source revalidation and independent Gaussian evaluation. |
| Cleaning validates consistency, not physical event identity | `sec:data-cleaning-validation` and results section 5.4 | Retained: finite extremes stay, invalid/duplicate/missing observations follow explicit rules, synthetic corruption tests do not alter the accepted real sample. |
| Gaussian fit, AIC, rarity and zero empirical exceedance do not validate candidate causes | `sec:resultados-estatisticos` | Retained with the numerical findings: 88/90 rejections, qualified Gaussian comparison, relative AIC versus absolute adequacy and Wilson uncertainty. |
| Internal cluster indices describe geometry under method-specific populations and eligibility | `sec:comparacao-clusterizacao` | Retained: fixed k, DBSCAN noise exclusion, missing scores, small hierarchical tails and differing index rankings; removed only the repeated final generic causal warning. |
| MAD shape association does not establish cause; exploratory comparison lacks multiplicity correction | `sec:evidencias-anomalia` | Retained immediately beside candidate counts and distribution-shape discussion. |
| Across-N sources are not demonstrated independent or nested; narrower zero-event intervals do not prove convergence | `sec:convergencia-amostral` | Retained with observed rates and observational comparison, including no optimal-N claim. |
| Controlled perturbations and Jaccard stability do not establish accuracy on real ATP errors | `sec:avaliacao-controlada` and `sec:discussao-resultados` | Retained beside benchmark and sensitivity findings, including restricted reference-group scope. |
| Reduced integration-step convergence alone does not validate the physical model | Methodological technical-review protocol | Retained as an investigation-specific condition, distinct from the actual missing-review status. |

### Changes and preservation review

- Removed repeated generic causal/specialist boilerplate from introduction,
  research problem, justification, reproducibility, parser/structure results,
  conversion acceptance, candidate-results opening, discussion and conclusion.
- Scope now states exclusions once; limitations now own the actual missing
  electrical evidence and unresolved package status. Three new labels support
  explicit links: `sec:escopo-limites`, `sec:camadas-validade` and
  `sec:alcance-limitacoes`. Existing `sec:lacunas-pacote` remains stable.
- Before/after source comparison confirms the ordered citation commands,
  `input` inclusions and asset references are identical. Equations, raw
  numerical results, table/figure sources and existing labels are preserved.
- No statistical finding is promoted to a causal electrical conclusion.
  Unresolved cases stay unresolved, and the retained local caveats in the
  inventory were checked against the pre-edit manuscript.
- This does not implement the T8 conclusion rewrite or claim T12 final-layout
  acceptance. Existing chart/table issues remain assigned to T9–T12.

### Verification

- Editorial gate: `just build` passes; final PDF has 79 pages. Final
  `doc/build/main.log` contains no LaTeX warnings, undefined references,
  missing files or overfull boxes.
- Visual review used Poppler renders and inspected physical PDF pages
  15–18, 38–46, 58, and 67–73 (printed page number is one lower). These
  cover the edited introduction/scope, methodology, extraction/conversion,
  candidate discussion, technical-review transition, limitations and
  conclusion. A newly isolated trailing word before section 5.11.1 was
  removed; final PDF pages 70–71 were re-rendered and inspected. Authored
  passages and resolved section numbers are readable without clipping.
- Existing landscape tables remain wide and repetitive; their redesign and
  complete placement acceptance belong to T11/T12, not this task.
- Required pre-commit Taskipy checks: format and lint pass without changing
  any Python file; `uv run task test` reports 327 passed in 76.72 seconds,
  with no failures or skips.
