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

## T3 — Appendix ownership of reproduction records (READ-03)

Executed on 2026-10-27 after T1 (`ac16319`). This editorial task relocates
audit logistics within `doc/main.tex`; it does not rerun scientific
experiments or regenerate evidence. No software, raw inputs, generated
tables, images or template assets changed.

### Relocation and preservation inventory

| Record | Original main-text owner | Appendix owner and retained main-text content |
| --- | --- | --- |
| Historical parser software acceptance: 100 tests, Ruff, BasedPyright | Extraction results | `app:historico-parser` (A.1); exact header, switching/maxima checkpoints and 235-file/533,450-run reconciliation remain in results. |
| CRPI correction and 10 September structural revalidation | Structure results, repeated historical remarks | A.1 retains the defect, fix, date, report/manifest locations and mandatory regeneration of old CRPI exports; main text retains exhaustive structural versus selected phase-A numerical coverage. |
| Exact `T_MAN/{SRPI,CRPI}/CASO-COMPLETO/SDEF` source directory | Extraction methodology and P.U. results | A.1 identifies the directory; main text still specifies complete, no-defect cases, both scenarios and all five sample sizes. |
| Electrical model file and line locations | P.U. methodology and conversion example | `app:fontes-eletricas` (A.2) retains the ANAFAS path, lines 34/38, ATP lines 392–395/330–333, LIS lines 3095/3262/3323/3383 and example line 1789. Main text retains the full 138 kV RMS-to-peak derivation, both voltage bases, rounding error, polarity convention and continuous-time limitation. |
| Original switching command `$DEPOSIT, SIGMAX=3.0` | Model/manoeuvre chapter | A.2 preserves exact command, SRPI complete case and 10,000-run identity; model chapter retains the switching interpretation and points to A.2. No output-voltage detector returns. |
| P.U. acceptance date, historical checks and former 100000 V configuration | Conversion results | `app:auditoria-pu` (A.3) retains 11 September date, 60/90 accepted comparisons, original software checks, revision hash, commands, artifact names, old 230000 V threshold mapping and correction history. Main text retains tolerances of 1e-12/1e-7 P.U., current 112677 V base, 12.677% comparison, current threshold equivalent and acceptance boundaries. |
| Detailed v3 paths repeated beside individual results | Probability, adequacy, distribution comparison, clustering, candidates, sample-size comparison, benchmark, sensitivity, discussion and package limits | `app:pacote-evidencias` (A.5) defines one package root and catalogs exact relative table/source/manifest paths. Main text retains all results and local qualifications; cross-references resolve. Figure legends retain immediate source filenames, interpreted relative to the same package root. |
| v2 generation date and GTPPLOT PDF filename | Statistical results and GTPPLOT discussion | A.5 retains 21 October 2026 historical date and `2000-N4-Estati-1.pdf`; current results use v3 and the GTPPLOT citation/interpretation stays with its scientific claims. |
| Existing audit commands, manifests, full revision hash, cleaning evidence | Existing appendix | Preserved in A.3/A.4; no audit evidence removed. |

### Verification

- `just build` passes, 79 pages. Final log has no LaTeX warnings,
  unresolved citations/references, missing files or overfull boxes.
- Automated before/after comparison confirms identical ordered sequences
  of 44 citation commands, six input inclusions, 13 graphics and all
  12 equation blocks. No existing label was removed; four appendix labels
  were added. File-line references, commands, hashes, dates and historical
  acceptance counts were compared against the relocation inventory above.
- Poppler-rendered physical PDF pages 35–37, 44–46, 52–53, 58, 69–70 and
  77–79 were inspected. Printed page numbers are one lower. New appendix
  sections, paths, commands, electrical line references and A.1–A.5 links
  are readable without clipping. Existing long tables/forced page breaks
  remain assigned to T9–T12; this is not whole-document layout acceptance.
- Required pre-commit Taskipy format and lint pass with no Python changes.
  The default uv cache is read-only in this environment; checks use
  `UV_CACHE_DIR=/tmp/uv-cache`.
- `uv run task test` passes: 327 passed in 76.65 seconds, no failures
  or skips. `git diff --check` passes. No SPEC_DEVIATION.


## T4 — Theory paragraph roles (READ-04)

Executed on 2026-10-27 after T3 (`f0467e5`). The change inserts 29 semantic
paragraph boundaries within the theoretical-foundation chapter. No words,
scientific claims or commands are added, removed or reordered.

### Paragraph-purpose inventory

| Topic | Roles now separated |
| --- | --- |
| Electrical systems and energization | System/line context; switching events; cited insulation implications; transient definition; energization dependencies; cited ATP/EMTP application. |
| ATP and data extraction | Tool capabilities; cited real-network application; cited line-model discussion; relevance of model quality to this study. |
| Statistical and probabilistic analysis | Statistical purpose; descriptive measures; caution about interpreting outliers separated from the confidence-expression definition. |
| Visualization | Exploratory/literature rationale; scatter-plot definition; study attributes; conceptual illustration; application before/after analysis. |
| Anomaly detection and learning | General anomaly definition; study context; interpretation caution; learning definition; learning families; unsupervised application; domain literature; transfer to this study. |
| Clustering | Similarity-based definition; application to simulated overvoltages. |
| K-Means | Historical literature; partition/iteration/objective definition; cited practical strengths; fixed-k limitation; cited illustration; geometric interpretation; study application. |
| DBSCAN | Origin and density-based principle; parameters/neighborhood; point classes; expansion procedure; cited comparison; anomaly-detection rationale; study application; interpretation caution; parameter/density limitations. |

### Preservation and editorial review

- Whitespace-normalized before/after comparison of the entire manuscript is
  exactly equal. Every word, citation, equation, label, figure and inclusion
  remains in the same order with the same content. Citations therefore stay
  attached to their original supported claims, and all local caveats remain.
- Boundaries follow changes of explanatory purpose rather than a word limit.
  Equation introductions and definitions stay linked. The original theory
  argument still runs from electrical phenomena through simulation,
  statistics/visualization and unsupervised pattern analysis to methodology.
- Terminology, future-tense procedures and conceptual-figure curation remain
  assigned to T5, T6 and T10 respectively. Existing float/reflow issues,
  including the DBSCAN figure interrupting the limitations paragraph, remain
  assigned to final integrated placement in T12.

### Verification

- `just build` passes: 79 physical PDF pages; final LaTeX log has no actual
  warnings, unresolved references/citations, missing assets or overfull boxes.
- Poppler-rendered physical PDF pages 19–30 (printed pages 18–29) inspected.
  All affected theoretical sections show readable paragraph boundaries,
  intact equations/citations and no clipping.
- Required pre-commit Taskipy checks: format and lint pass with no Python
  changes; `uv run task test` reports 327 passed in 73.54 seconds, no
  failures or skips.


## T5 — Terminology and acronym consistency (READ-05)

Executed on 2026-10-27 after T4 `1a13400`, by the fourth distinct sequential
implementation agent. This task changes manuscript terminology and task/state
tracking only; software, raw inputs and published evidence remain unchanged.

### Term inventory and first-use review

| Term | Definition or editorial rule | First substantive location |
| --- | --- | --- |
| SRPI / CRPI | Without / with pre-insertion resistor; preserve actual switching scenario names | Section 3.6, before the first SRPI model-specific claim; acronym list |
| P.U. | Por unidade, from *per unit*; ratio to the declared voltage base | Methodology opening; normalization heading and acronym list |
| MAD | Desvio absoluto mediano, from *median absolute deviation* | Theory section 2.3; explicit formula remains in 4.6.3; acronym list |
| AIC | Critério de informação de Akaike, from *Akaike information criterion* | Exploratory distribution-family comparison in 5.5.1; acronym list |
| Computational routine | Implemented extraction, processing and analysis sequence | Introduction/objective/conclusion aligned; explicit inventory in 4.6.1 |
| Model | Electrical network representation, or qualified statistical/clustering fit | 4.6.1 distinguishes these from the routine |
| Analysis group / clustering partition | Comparable observations under declared keys / algorithm-produced partition | 4.6.1; English cluster/cluster(s) prose replaced with agrupamento(s) |
| Candidate / applicability | Observation flagged by at least one applicable criterion / minimum calculation conditions satisfied | 4.6.1; non-applicability remains distinct from no candidates |
| Source lineage | Configured provenance identifier, scenario plus sample count in this package | 4.6.1; distinct from file path, content digest and observation identity |
| Centroide(s) | Standard Portuguese spelling without accent | Theory prose, schematic node labels, captions, methodology and results |
| Parser / outliers / seed / hash / pipeline | Define leitor estruturado and valores atípicos at first substantive use; explain pseudo-random seed; use resumo SHA-256 and fluxo computacional | Objective, theory and methodology; technical file/field/label identifiers preserved |

Acronym and symbol lists were reviewed; new acronym entries are ordered and
fit one readable page. Existing symbols and electrical equations are intact.
The abstract remains self-contained and spells out the resistor scenarios.

### CodeNavi source-lineage verification

The following current owners establish metadata semantics, rather than an
inferred genealogical or independence relationship:

- `scripts/build_defense_evidence.py:_run_source_phases()` constructs each
  source lineage from lowercase scenario and sample size and records the
  manifest's content digest separately.
- `src/services/config.py:AnalysisConfig` declares contextual grouping as
  scenario, source lineage, terminal and phase.
- `src/services/preprocessing.py:extract_maxima()` preserves source file,
  simulation, terminal and phase separately; a missing lineage defaults to
  the file identifier in the generic preprocessing helper.
- `src/services/controlled_benchmark_runner.py:_split_by_source_run_block()`
  partitions whole lineage/simulation keys, preserving terminal/phase peers.

The manuscript defines the actual package policy and does not claim that
lineage proves independence or nested simulations. Technical code-location
pointers stay here; no reproduction commands were moved back into the main
argument. Existing notebook flow pointers were consulted; no duplicate
notebook note is needed because this report now owns the terminology audit.

### Verification

- Editorial gate: `just build` passes, 80 physical PDF pages. The added
  definitions move the methods/results boundary by one page; they are not
  hidden by shrinking fonts. The final LaTeX log has no actual warnings,
  undefined references/citations, missing files or overfull boxes.
- Preservation comparison with T4: all 44 citation commands, 6 input
  inclusions, 13 graphics, 12 equation blocks and 39 labels are identical.
  Existing raw values, table assets and bibliography keys are unchanged.
- Searches confirm no accented centroide spelling, standalone English
  cluster/cluster(s), pipeline or hashes remains in authored prose. Existing
  technical label identifiers containing cluster remain unchanged.
- Physical PDF pages 9, 23–24, 27, 35–36, 39–41, 53 and 72 were rendered
  and inspected. The acronym list and lineage definition were also inspected
  individually at readable size. Captions, schematic labels, acronym first
  uses and definitions fit without clipping. P.U. wording was refined to
  “por unidade”; the affected acronym/methodology pages were rebuilt and
  rechecked (physical PDF pages 9, 36–37). Printed page numbers are one lower
  after front matter.
- Required pre-commit Taskipy format and lint checks pass without changing
  Python files; `uv run task test` reports 327 passed in 74.19 seconds,
  with no failures or skips.
- No SPEC_DEVIATION. T6 owns verb-tense alignment; T8 owns conclusion
  restructuring; T9–T12 retain numeric, figure/table and integrated-layout
  work. This task does not close pending electrical review.
