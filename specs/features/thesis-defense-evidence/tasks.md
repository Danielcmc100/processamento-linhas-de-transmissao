# Thesis Defense Evidence Package Tasks

**Design:** `specs/features/thesis-defense-evidence/design.md`
**Status:** In Progress
**Baseline:** 112 tests pass; typecheck has 4 pre-existing visualization errors

## Execution plan

```text
Phase 1: T1 [P]   T2 [P]   T3 [P]
             \      |      /
Phase 2:     T4 [P] T5 [P] T6 [P]
               \     |     /
Phase 3:          T7
              /    |    \
Phase 4: T8 [P]  T9 [P]  T10 [P]
              \    |    /
Phase 5: T11 [P] T12 [P] T13 [P]
              \    |    /
Phase 6: T14 [P] T15 [P] T16 [P]
                  |
Phase 7:         T17
                  |
Phase 8:     T18 -> T19 -> T20
```

## Task breakdown

### T1: Preserve complete observation identity [P]

**What:** Preserve signed source voltage and explicit experiment identity.
**Where:** `src/services/schemas.py`, `src/services/preprocessing.py`,
`tests/test_preprocessing.py`
**Depends on:** None
**Reuses:** Existing `MaximaObservation` and loader contracts
**Requirements:** DEF-03, DEF-17
**Tests:** unit
**Gate:** `uv run pytest tests/test_preprocessing.py -q`
**Done when:** Signed value, scenario, size, lineage, base, and event definition
survive extraction; existing keys remain stable; at least 8 preprocessing tests
pass.
**Commit:** `feat(evidence): preserve complete observation identity`

### T2: Build canonical dataset manifest [P]

**What:** Discover and validate ten SRPI/CRPI scenario-size sources.
**Where:** `src/services/dataset_manifest.py`,
`tests/test_dataset_manifest.py`
**Depends on:** None
**Reuses:** Source hashing and parser declarations
**Requirements:** DEF-01, DEF-02
**Tests:** unit/integration
**Gate:** `uv run pytest tests/test_dataset_manifest.py -q`
**Done when:** All ten sources, 112677 V, counts, hashes, coverage, assumptions,
and exclusions are deterministic; invalid base/provenance tests fail closed.
**Commit:** `feat(evidence): add canonical dataset manifest`

### T3: Add descriptive and empirical probability evidence [P]

**What:** Produce scoped descriptives, strict exceedance, and Wilson interval.
**Where:** `src/services/statistical_evidence.py`,
`tests/test_statistical_evidence.py`
**Depends on:** None
**Reuses:** `src/services/statistics.py`
**Requirements:** DEF-04, DEF-05
**Tests:** unit
**Gate:** `uv run pytest tests/test_statistical_evidence.py -q`
**Done when:** Counts, denominator, mean, sample SD, median, quartiles,
percentiles, min/max, probability, percentage, CI, scope, and boundary cases
are tested; at least 7 tests pass.
**Commit:** `feat(statistics): add empirical probability evidence`

### T4: Add Gaussian adequacy and robust baseline [P]

**What:** Evaluate Anderson-Darling adequacy and MAD evidence.
**Where:** `src/services/distribution_adequacy.py`,
`tests/test_distribution_adequacy.py`
**Depends on:** T3
**Reuses:** Gaussian fit and SciPy statistics
**Requirements:** DEF-07, DEF-25
**Tests:** unit
**Gate:** `uv run pytest tests/test_distribution_adequacy.py -q`
**Done when:** Normal, skewed, heavy-tail, multimodal, undersized, and constant
fixtures return explicit decisions, diagnostics, empirical/model differences,
and robust applicability; at least 8 tests pass.
**Commit:** `feat(statistics): qualify Gaussian and robust evidence`

### T5: Parse and reconcile ATP probability tables [P]

**What:** Parse ATP bins and reconcile direct counts with printed precision.
**Where:** `src/parser/statistical_distribution.py`,
`src/services/probability_reconciliation.py`,
`tests/test_probability_reconciliation.py`
**Depends on:** T3
**Reuses:** Existing LIS decoding conventions
**Requirements:** DEF-06
**Tests:** unit/integration
**Gate:** `uv run pytest tests/test_probability_reconciliation.py -q`
**Done when:** Source and recalculated values, operator, tolerance, boundary,
and invalid/qualified status are preserved; at least 5 tests pass.
**Commit:** `feat(statistics): reconcile ATP probability tables`

### T6: Add contextual K-Means evidence [P]

**What:** Emit descriptive labels plus group-local distance evidence.
**Where:** `src/services/kmeans_evidence.py`,
`tests/test_kmeans_evidence.py`
**Depends on:** T1
**Reuses:** `cluster_kmeans()` grouping/order patterns
**Requirements:** DEF-08, DEF-09
**Tests:** unit
**Gate:** `uv run pytest tests/test_kmeans_evidence.py -q`
**Done when:** Upper dense clusters remain valid, isolated points may flag,
threshold metadata is recorded, sparse/constant groups are non-applicable,
and at least 6 tests pass.
**Commit:** `feat(anomaly): add contextual K-Means evidence`

### T7: Add calibrated DBSCAN evidence

**What:** Emit scaled group-local DBSCAN evidence and diagnostics.
**Where:** `src/services/dbscan_evidence.py`,
`tests/test_dbscan_evidence.py`
**Depends on:** T1
**Reuses:** DBSCAN primitive and row-order restoration
**Requirements:** DEF-10
**Tests:** unit
**Gate:** `uv run pytest tests/test_dbscan_evidence.py -q`
**Done when:** Effective epsilon, parameter source, clusters, noise count/rate,
and applicability are explicit; all-noise/constant/sparse groups do not vote;
at least 6 tests pass.
**Commit:** `feat(anomaly): add calibrated DBSCAN evidence`

### T8: Correct method comparison [P]

**What:** Compare only explicit applicable Boolean criteria.
**Where:** `src/services/comparison.py`, `tests/test_comparison.py`
**Depends on:** T4, T6, T7
**Reuses:** Stable reason serialization
**Requirements:** DEF-08, DEF-11, DEF-15
**Tests:** unit
**Gate:** `uv run pytest tests/test_comparison.py -q`
**Done when:** Labels cannot change flags, non-applicable methods do not count,
reasons list met criteria only, disagreement remains visible, and at least 8
tests pass.
**Commit:** `fix(anomaly): remove cluster-label anomaly inference`

### T9: Generate controlled perturbations [P]

**What:** Create deterministic copied-data interventions and lineage-safe split.
**Where:** `src/services/perturbations.py`, `tests/test_perturbations.py`
**Depends on:** T1
**Reuses:** Observation identity contract
**Requirements:** DEF-12
**Tests:** unit
**Gate:** `uv run pytest tests/test_perturbations.py -q`
**Done when:** Clean, point, contextual, collective, 1/5/10%, seed, intensity,
unchanged originals, and no split leakage are tested; at least 7 tests pass.
**Commit:** `feat(anomaly): add controlled perturbation generator`

### T10: Preserve signed technical review records [P]

**What:** Select review strata and serialize causal-status records.
**Where:** `src/services/technical_review.py`,
`tests/test_technical_review.py`
**Depends on:** T1, T8
**Reuses:** Switching loader and explicit method evidence
**Requirements:** DEF-17, DEF-26
**Tests:** unit
**Gate:** `uv run pytest tests/test_technical_review.py -q`
**Done when:** All required fields and categories round-trip; missing causal
evidence forces unresolved; unavailable repeat simulation is explicit; at least
5 tests pass.
**Commit:** `feat(review): add traceable technical review records`

### T11: Measure controlled benchmark [P]

**What:** Compute confusion counts and safe performance metrics.
**Where:** `src/services/benchmark.py`, `tests/test_benchmark.py`
**Depends on:** T8, T9
**Reuses:** Controlled labels and method flags
**Requirements:** DEF-13
**Tests:** unit
**Gate:** `uv run pytest tests/test_benchmark.py -q`
**Done when:** TP/FP/TN/FN precede precision/recall/F1/FPR, zero denominators
are null with reasons, and independent recomputation matches; at least 6 tests
pass.
**Commit:** `feat(anomaly): add controlled benchmark metrics`

### T12: Evaluate convergence and method matrix [P]

**What:** Compare compatible sample sizes, scenarios, terminals, phases, methods.
**Where:** `src/services/convergence.py`,
`tests/test_convergence.py`
**Depends on:** T2, T3, T4, T8
**Reuses:** Manifest compatibility and evidence tables
**Requirements:** DEF-14, DEF-15
**Tests:** unit
**Gate:** `uv run pytest tests/test_convergence.py -q`
**Done when:** Five sizes, missing coverage, deltas, CI width, method status,
high-sample wording, and incompatible-base rejection are tested; at least 6
tests pass.
**Commit:** `feat(evidence): add convergence and method matrix`

### T13: Evaluate parameter sensitivity [P]

**What:** Replay frozen grids and compute identity Jaccard stability.
**Where:** `src/services/sensitivity.py`,
`tests/test_sensitivity.py`
**Depends on:** T6, T7, T8
**Reuses:** Stable observation keys and method configuration IDs
**Requirements:** DEF-16
**Tests:** unit
**Gate:** `uv run pytest tests/test_sensitivity.py -q`
**Done when:** Seeds, ranges, controls, counts, rates, applicability, overlap,
same-rate/different-identity behavior, and sensitivity status are reproducible;
at least 6 tests pass.
**Commit:** `feat(anomaly): add parameter sensitivity evidence`

### T14: Generate traceable defense tables [P]

**What:** Export source CSV and deterministic Brazilian Portuguese LaTeX tables.
**Where:** `src/services/defense_reporting.py`,
`tests/test_defense_reporting.py`
**Depends on:** T10, T11, T12, T13
**Reuses:** Existing safe writer and JSON formatting
**Requirements:** DEF-19, DEF-27
**Tests:** unit/integration
**Gate:** `uv run pytest tests/test_defense_reporting.py -q`
**Done when:** Probability, benchmark, convergence, and review tables preserve
source precision, rounding policy, trace keys, and Portuguese labels; at least
6 tests pass.
**Commit:** `feat(reporting): generate traceable defense tables`

### T15: Generate publication figures [P]

**What:** Render saved evidence sources into accessible publication figures.
**Where:** `src/services/defense_visualization.py`,
`tests/test_defense_visualization.py`
**Depends on:** T10, T11, T12, T13
**Reuses:** Matplotlib primitives and saved source tables
**Requirements:** DEF-18, DEF-27
**Tests:** unit/smoke
**Gate:** `uv run pytest tests/test_defense_visualization.py -q`
**Done when:** Required plots expose scope, thresholds, applicability, distinct
cluster/anomaly encodings, SVG and 300 DPI PNG, Portuguese labels, and at least
6 tests pass.
**Commit:** `feat(reporting): generate publication defense figures`

### T16: Build claim and reproducibility manifests [P]

**What:** Index requirements, claims, sources, outputs, hashes, and semantics.
**Where:** `src/services/reproducibility.py`,
`tests/test_reproducibility.py`
**Depends on:** T2, T10, T11, T12, T13
**Reuses:** Existing SHA-256 and software-version metadata
**Requirements:** DEF-22, DEF-23
**Tests:** unit/integration
**Gate:** `uv run pytest tests/test_reproducibility.py -q`
**Done when:** Code revision, dependencies, commands, hashes, statuses,
nondeterministic exclusions, schema rejection, and semantic equality are
tested; at least 7 tests pass.
**Commit:** `feat(evidence): add reproducibility and claim manifests`

### T17: Integrate defense evidence pipeline

**What:** Run validated observations through all evidence components without
automatic candidate removal.
**Where:** `src/services/config.py`, `src/services/pipeline.py`,
`src/services/reporting.py`, `tests/test_pipeline.py`,
`tests/test_reporting.py`
**Depends on:** T4, T5, T8, T11, T12, T13, T14, T15, T16
**Reuses:** Current pipeline and overwrite policy
**Requirements:** DEF-01 through DEF-19, DEF-22, DEF-23
**Tests:** integration
**Gate:** `uv run pytest tests/test_pipeline.py tests/test_reporting.py -q`
**Done when:** Primary statistics use validated rows, candidates remain
reversible, new artifacts are source-first/versioned, old schemas fail closed,
and at least 9 integration tests pass.
**Commit:** `feat(pipeline): integrate defense evidence package`

### T18: Complete manuscript methodology

**What:** Replace methodology TODOs with frozen Brazilian Portuguese methods.
**Where:** `doc/main.tex`
**Depends on:** T17
**Reuses:** Existing thesis structure and accepted validation prose
**Requirements:** DEF-20, DEF-27
**Tests:** document build
**Gate:** `cd doc && latexmk -pdf -interaction=nonstopmode -file-line-error main.tex`
**Done when:** Scope, probability, adequacy, anomaly, controlled benchmark,
convergence, sensitivity, review, and validity layers are defined; no required
methodology TODO remains; PDF builds.
**Commit:** `docs(thesis): complete defense methodology`

### T19: Generate evidence and complete results

**What:** Build target-data package and write evidence-derived results,
discussion, limitations, and conclusion in Brazilian Portuguese.
**Where:** `scripts/build_defense_evidence.py`,
`results/defense-evidence/v1/`, `doc/main.tex`
**Depends on:** T18
**Reuses:** Integrated evidence pipeline and generated tables/figures
**Requirements:** DEF-21, DEF-27
**Tests:** integration/document
**Gate:** Full software gate plus LaTeX build
**Done when:** Ten-source matrix and permitted analyses run; missing electrical
review remains unresolved; claims cite artifacts; conclusion answers objectives
without causal or insulation recommendation overreach.
**Commit:** `docs(thesis): add traceable defense results`

### T20: Verify final package

**What:** Run all software, artifact, language, reference, and document gates.
**Where:** `specs/features/thesis-defense-evidence/validation.md`,
`specs/features/thesis-defense-evidence/spec.md`,
`specs/project/STATE.md`, `.notebook/`
**Depends on:** T19
**Reuses:** Requirement IDs and package manifest
**Requirements:** DEF-24
**Tests:** full
**Gate:** `task format`, `task lint`, `task typecheck`, `task test`, LaTeX build
**Done when:** Gate results and test delta are recorded, each requirement has a
verified/blocked status, package status matches evidence, and no unsupported
claim is marked accepted.
**Commit:** `docs(evidence): verify thesis defense package`

## Granularity check

| Task | Atomic deliverable | Status |
|---|---|---|
| T1-T7 | One contract or analytical method each | Pass |
| T8-T13 | One comparison/experiment product each | Pass |
| T14-T16 | One publication/package product each | Pass |
| T17 | One integration boundary | Pass |
| T18-T20 | One manuscript or verification stage each | Pass |

## Diagram-definition cross-check

| Tasks | Body dependencies | Diagram | Status |
|---|---|---|---|
| T1-T3 | None | Phase 1 roots | Match |
| T4-T6 | T3/T1 | Phase 2 after foundation | Match |
| T7 | T1 | Phase 3 before comparison | Match |
| T8-T10 | T1/T4/T6/T7 | Phase 4 | Match |
| T11-T13 | Evidence foundations | Phase 5 | Match |
| T14-T16 | Final analytical tables | Phase 6 | Match |
| T17 | T4-T16 products | Phase 7 | Match |
| T18-T20 | Sequential integration | Phase 8 | Match |

## Test co-location validation

| Tasks | Layer | Matrix requires | Task says | Status |
|---|---|---|---|---|
| T1-T16 | Service/parser | Unit; integration across boundaries | Co-located unit/integration | Pass |
| T17 | Cross-layer pipeline | Integration | Integration | Pass |
| T18-T19 | Manuscript/artifacts | Build/integration | Document + full gate | Pass |
| T20 | Final feature | Full build | Full | Pass |

## Tool assignment

- MCP: none required; local source and data are authoritative.
- Skills: `tlc-spec-driven` orchestrates execution; `codenavi` governs
  repository exploration and surgical changes.
- Tools: `apply_patch`, `rtk`, `uv`, pytest, Ruff, BasedPyright, latexmk.
- Parallel tasks use one sub-agent per `[P]` task. Orchestrator alone commits
  task-scoped files to avoid shared-index races.
