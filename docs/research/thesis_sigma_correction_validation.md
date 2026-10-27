# Thesis Sigma Correction Validation

## T7.1 — Retire the voltage detector and comparison criterion

Date: 2026-10-26. Scope: READ-07, T7.1 only. Remaining subtasks are
not implemented or validated by this report.

### Contract and ownership

- `src/services/pipeline.py:run_pipeline()` now sends validated observations
  directly to MAD evidence evaluation. `_add_sigma_evidence()` and its call
  were removed, including their now-unused imports. Annotated observations
  no longer acquire sigma thresholds, adequacy decisions, applicability,
  flags, or reasons.
- `src/services/comparison.py:_METHODS` now contains only MAD modified Z,
  K-Means distance, and DBSCAN noise, in that deterministic reason order.
  Existing applicability validation and aggregation rules are unchanged.
  Hierarchical and other cluster labels remain non-voting.
- Comparison preserves input columns and row order. Retired sigma columns
  supplied by an external caller are ignored, not validated or counted.
  They are not stripped from arbitrary input; the active pipeline no longer
  generates them. No compatibility switch or replacement detector was added.
- Summary sigma thresholds and plotting markers remain owned by T7.2.
  Gaussian adequacy evaluation, mean/sample deviation, MAD calculations,
  switching inputs, and historical evidence were not changed.

### Fresh baseline

Captured before editing implementation or tests, not copied from historical
testing documentation:

| Command | Result |
| --- | --- |
| `uv run task test` | 309 passed, 16.10 s |
| `uv run task lint` | Passed |
| `uv run task typecheck` | 0 errors, 0 warnings, 0 notes |
| `uv run ruff format --check .` | 168 files already formatted |

The baseline used a read-only formatting check to avoid editing user files.
`uv` reports an unrelated inherited `VIRTUAL_ENV` and explicitly uses this
repository's `.venv`; this warning occurred throughout verification.

### Tests first: RED, then GREEN

Updated owning tests before implementation:

- `tests/test_comparison.py`: three-method fixture; exact votes,
  applicability denominators, positive union, disagreement and reason order;
  unchanged full input rows; hierarchical label independence; zero applicable
  methods; all three single-method cases with both positive and negative
  evidence; retired sigma fields ignored even with invalid legacy types.
  Existing invalid-state and empty-schema coverage remains.
- `tests/test_pipeline.py`: no sigma-prefixed observation columns or sigma
  reasons, retained remaining evidence, at most three applicable methods,
  and existing end-to-end observation identity and analysis outputs.

RED command: `uv run pytest tests/test_comparison.py tests/test_pipeline.py`.
Result: **24 failed, 2 passed**, 4.10 s. Comparison failed because sigma
columns were still mandatory; pipeline failed because sigma columns still
existed. The subsequent unanalyzable-selection test also failed because the
first integration assertion interrupted figure cleanup. This secondary RED
failure disappeared after the implementation passed its assertions.

After removing the detector and criterion, the same command passed all
**26 tests** (initial GREEN: 3.79 s; final rerun: 4.53 s).

Count reconciliation: two obsolete sigma-column-required parameter cases
were retired; six single-applicable-method cases and one ignored-legacy-
sigma case were added. Net increase: five tests, from 309 to 314 overall.
No unrelated test was removed, skipped, or disabled. Behavioral assertions
were not changed after RED. Subsequent test edits were formatting and an
explicit integer type guard for the existing maximum-count assertion.

### Final software gates

| Command | Result |
| --- | --- |
| `uv run task format` | Passed; 168 files unchanged on final run |
| `uv run task lint` | Passed |
| `uv run task test` | 314 passed, 15.51 s |
| `uv run task typecheck` | 0 errors, 0 warnings, 0 notes |
| `uv run pytest tests/test_comparison.py tests/test_pipeline.py` | 26 passed |

An initial formatting gate caught an overlong new test signature; formatting
was repaired. An initial typecheck caught Polars' broad scalar return type
for `Series.max()` in the new pipeline assertion. An integer type assertion
was added before the unchanged `<= 3` check. All gates above were rerun.

### Explicit downstream contract failure — T7.3

The green suite is not proof that publication works with the new output.
A separate local fixture probe ran `run_pipeline()` using
`tests/test_pipeline.py:_config()` in a temporary directory, closed its
figures, added a synthetic `terminal_position_km=0.0` column solely to
isolate the method contract (the publication builder normally adds terminal
positions), then called `convergence.py:build_method_comparison_matrix()`.

The probe exited **1** with:

```text
ValueError: Missing method comparison columns: sigma_flag, sigma_applicability, sigma_reason.
```

Failure ownership: `src/services/convergence.py:_METHOD_COLUMNS` still
requires those three fields, and `build_method_comparison_matrix()` still
declares four `compared_methods`. `defense_reporting.py` also retains its
sigma reason label. These consumers and their fixtures belong to T7.3;
they were inspected but not edited. Their current tests do not exercise
the new pipeline-to-consumer boundary. No exception was suppressed and no
legacy fields were reintroduced to make the probe pass.

Assessment: T7.1's owned contract is verified and can be committed under the
task's explicit intermediate-failure allowance. Evidence generation and
publication must wait for T7.2 and T7.3. No real-data regeneration, manuscript
publication, or complete READ-07 claim is made here.

### Handoff and lessons

- T7.2 owns `statistics.py`, `schemas.py`, `visualization.py`, their callers
  and tests; retain Gaussian diagnostics and independent statistical uses.
- T7.3 must reconcile the method matrix's required columns and method names,
  reporting consumers, fixtures, and publication routing before generation.
- Full-suite success can coexist with a broken newly changed producer-to-
  consumer contract when consumers use legacy fixtures; keep the explicit
  boundary probe in the handoff.
- `.notebook/clustering-anomaly-flow.md` contains historical statements that
  predate the existing explicit-vote design. Source inspection, not that
  note's sigma flow or label-voting description, determined this change.
  This report records the current pointers without duplicating them in an
  additional notebook entry; notebook cleanup is outside this task's scope.
- User-authored plans, `specs/project/STATE.md`, and the visual review were
  preserved and excluded from the commit. Task tracking remains with the
  orchestrator.

**SPEC_DEVIATION:** None. The documented downstream failure is explicitly
permitted by T7.1 and remains assigned to T7.3.

## T7.2 — Remove voltage-sigma summary and plot outputs

Date: 2026-10-26. Scope: READ-07, T7.2 only, following T7.1 commit
`81b633b`. The inherited verified baseline is 314 passing tests. This task
does not complete READ-07, regenerate evidence, or publish manuscript assets.

### Contract and caller classification

- `statistics.py:summarize_statistics()` and
  `schemas.py:StatisticalSummaryRow` no longer produce or declare
  `sigma_3_threshold`, including empty and unestimable summaries.
  Mean, sample deviation (`ddof=1`), empirical exceedance, Gaussian tail
  estimates, and explicit validation statuses retain their computations.
- Removed `statistics.py:sigma_summary()`,
  `GaussianFitResult.sigma_level()`, and `schemas.py:SigmaSummaryRow`.
  Repository caller search found only the table-to-threshold helper chain
  and its detector-specific unit tests; no independent production caller
  justified retaining this voltage-threshold table API.
- Retained `fit_gaussian()` and `GaussianFitResult`: callers include
  `distribution_adequacy.py`'s qualified Gaussian probability comparison,
  `pipeline.py:_build_plot_fits()`, and
  `visualization.py:plot_pdf_overlay()`. Retained
  `exceedance_probability()` serves adequacy comparison and the existing
  DBSCAN-selected observation annotations in `plot_exceedance_curve()`;
  those markers are not voltage-sigma screening lines.
- `visualization.py:plot_pdf_overlay()` retains the Gaussian PDF and one
  solid mean marker, removing both dashed three-deviation voltage markers.
  `plot_combined()` inherits this behavior. The PDF's four-standard-deviation
  evaluation extent is retained solely as a curve-domain choice, not a
  detector threshold, annotation, or vote. Empty, insufficient, non-finite,
  and constant samples no longer render invalid fitted overlays; finite
  observations remain usable in mixed samples.
- `pipeline.py:run_pipeline()` passes the summary directly to
  `reporting.py:write_result_artifacts()`, which writes `summary.csv`
  without enumerating its columns. No caller implementation needed editing;
  the pipeline/CLI integration tests verify the changed in-memory and
  exported contracts. Generic reporting and schema tests also pass.
- MAD formulas, normality/adequacy implementations, raw ATP/LIS files,
  switching-time configuration and plotting, and historical outputs were
  not changed. Their retained references are not evidence of a remaining
  voltage-sigma detector. Active guidance/manuscript correction is T7.5.

### Tests first and software gates

Owning tests were changed before implementation. Two retired helper tests
were replaced with descriptive-fit/API and sigma-free-schema checks; the
Gaussian tail test supplies an independent voltage rather than calling a
threshold helper. Existing statistical assertions remain, except for
superseded threshold assertions. Added two summary edge-case tests and
seven plot cases: direct/combined marker content, empty/non-finite/singleton/
constant samples, and finite-only fitting. Integration checks cover summary
columns and the actual CLI-exported CSV. Net increase: nine tests, from
314 to 323; none skipped or disabled.

RED command: `uv run pytest tests/test_statistics.py
tests/test_visualization.py tests/test_pipeline.py`: **16 failed, 15 passed**,
4.25 s. Failures exposed the old columns, helper, extra markers, and invalid
overlays. The pipeline cleanup assertion also encountered open figures:
legacy visualization smoke tests leave figures open, and a failed pipeline
assertion prevents its own cleanup. The final targeted command uses normal
suite ordering (pipeline before visualization); no test was disabled or
weakened to hide the failure. Test changes after RED were formatting only.

| Command | Result |
| --- | --- |
| `uv run pytest tests/test_pipeline.py tests/test_statistics.py tests/test_visualization.py` | 31 passed, 3.72 s |
| `uv run task format` | Passed; 169 files unchanged on final run |
| `uv run task lint` | Passed |
| `uv run task test` | 323 passed, 14.10 s |
| `uv run task typecheck` | 0 errors, 0 warnings, 0 notes |

The first formatting run fixed import ordering and caught one overlong test
schema literal, then passed after wrapping it. The inherited unrelated
`VIRTUAL_ENV` warning persists; uv uses the repository environment.

### Explicit T7.3 boundary and handoff

Repeated the T7.1 fixture-to-method-matrix probe after T7.2 using a temporary
directory under `/tmp/opencode`, closing figures and adding only the
synthetic terminal-position column needed to isolate the contract. It again
exited **1**, without suppression:

```text
ValueError: Missing method comparison columns: sigma_flag, sigma_applicability, sigma_reason.
```

`convergence.py:build_method_comparison_matrix()` and downstream publication
remain T7.3 work. No compatibility columns were restored. No real-input
regeneration or publication was attempted. This report holds the investigated
caller pointers and gotchas rather than duplicating them in `.notebook/`;
the notebook index was read and its historical sigma flow was not trusted
over source. User-owned feature plans, project state, and visual-review notes
are excluded from this task's commit; tracking remains with the orchestrator.

**SPEC_DEVIATION:** None. T7.2's owned contracts and gates pass; the known
T7.3 integration failure remains explicit and unresolved.

## T7.3 — Align evidence consumers and publication routing

Date: 2026-10-26. Scope: READ-07, T7.3, following `661f791`.
The existing local implementation and tests were inspected and verified;
no additional production changes were required during this verification.

- `convergence.py:build_method_comparison_matrix()` requires only MAD,
  K-Means distance and DBSCAN noise evidence. Its declared method order
  matches comparison reasons. Historical sigma display translation was
  removed from `defense_reporting.py`.
- `build_defense_evidence.py` defaults to the new v3 directory and declares
  `defense-v3-three-methods` as the convergence method policy. The existing
  nonempty-output guard still prevents accidental historical overwrite.
  Existing schema/generator versions remain unchanged; the publication
  directory and method policy identify this evidence revision.
- `prepare_defense_document.py:main()` resolves each manuscript reference's
  explicit version, rather than hardcoding v2. Tests verify mixed explicit
  versions, preserved historical assets, and failure when a v3 source is
  absent instead of silently substituting v2.
- The integration fixture generates ten synthetic sources with 50 actual
  runs each and nominal canonical size labels. It exercises real parsing,
  pipeline analysis, consumers, benchmark, sensitivity, publication,
  reproducibility and asset copying. It does not establish real-data counts.
  Its 4,500 method rows reconcile exact applicability denominators, votes,
  union, disagreement and deterministic reasons; all 90 convergence groups
  reconcile candidate counts. Gaussian fit diagnostics remain available.
  Generated CSV and LaTeX artifacts contain no retired detector contract.
  Source/output hashes and output coverage match the reproducibility
  manifest. Electrical review remains incomplete.

| Command | Result |
| --- | --- |
| `uv run pytest -q tests/test_convergence.py tests/test_defense_reporting.py tests/test_build_defense_evidence.py tests/test_prepare_defense_document.py tests/test_reproducibility.py tests/test_technical_review.py` | 45 passed, 76.03 s |
| `uv run task format` | Passed; 170 files unchanged |
| `uv run task lint` | Passed |
| `uv run pytest -q` | 327 passed, 88.53 s; fresh orchestrator baseline of this unchanged software state |
| `uv run task typecheck` | 0 errors, 0 warnings, 0 notes outside sandbox |
| `git diff --check` | Passed |

The full suite has four additional cases relative to T7.2's 323 tests: a
v3-default check, complete synthetic publication integration, and two asset
copier checks. Existing convergence and technical-review fixtures now use
three criteria; no unrelated tests were deleted, skipped or disabled.
These tests were already present in the inherited local work; no new RED
claim is made in this verification pass.

Inside the sandbox, BasedPyright could not discover installed site-packages
and reported 183 missing-import errors, including Polars and Pytest. An
explicit interpreter did not repair that environment failure. The exact
Taskipy typecheck command passed when rerun outside the sandbox; no project
configuration or diagnostic suppression was added.

The formerly failing pipeline-to-matrix boundary now passes through the
complete fixture publication path. T7.4 owns real-data regeneration and
reconciliation; T7.5 owns manuscript publication and active guidance.

**SPEC_DEVIATION:** None.

## T7.4 — Regenerate and reconcile canonical evidence

Date: 2026-10-26. Scope: READ-07, T7.4, following `acd458d`.
Before generation, `results/defense-evidence/` contained only v1 and v2.
The following command completed successfully, without `--overwrite`:

```text
uv run python -m scripts.build_defense_evidence --output results/defense-evidence/v3
```

Matplotlib reported an unwritable user configuration directory and selected
a temporary cache under `/tmp`; generation completed with exit code zero.
No new ATP simulation or raw-input edit was performed.

### Publication and preservation checks

- All 3,743 input and historical v1/v2 files in the pre-generation SHA-256
  inventory retained their original hashes.
- The new reproducibility manifest passes
  `reproducibility.py:validate_reproducibility_manifest()`. All ten source
  hashes and all 609 output hashes match actual files. Its output list
  covers every package file except the manifest itself.
- The ten canonical dataset-manifest rows equal v2 exactly, including source
  paths, hashes, declared/effective run counts and electrical bases. Their
  204,300 accepted scalar observations are present in both the annotated
  table and method matrix; statistical denominators sum to 204,300.
- Every generated CSV was checked for retired sigma column names and the
  `sigma_3` reason; every generated LaTeX table was checked for sigma labels.
  None remains. Independently justified Gaussian diagnostics remain.
- For every method-matrix observation, independent recomputation from the
  three flags and applicability states matches applicable-method count,
  positive agreement, candidate union, disagreement and ordered reasons.
  Candidate counts independently grouped over all 90 electrical scopes
  equal the new convergence table.
- Package status remains `incomplete`, causal conclusion `unresolved`, and
  all five selected electrical-review records remain unresolved with no
  reviewer or completed review date. Synthetic benchmark results do not
  acquire causal labels.

### Complete source-table reconciliation against v2

All 13 source tables retain their row counts. Ten are exactly equal across
every field, rather than merely equal after display rounding:

| Unchanged source table | Rows |
| --- | ---: |
| `dataset_manifest.csv` | 10 |
| `statistical_evidence.csv` | 90 |
| `distribution_adequacy.csv` | 90 |
| `distribution_comparison.csv` | 270 |
| `clustering_comparison.csv` | 270 |
| `probability_reconciliation.csv` | 1,151 |
| `controlled_benchmark.csv` | 20 |
| `controlled_interventions.csv` | 2,592 |
| `sensitivity.csv` | 20 |
| `technical_review.csv` | 5 |

The remaining three tables account for every detected difference:

- `annotated_observations.csv` and `method_comparison.csv` each retain
  204,300 rows and remove `sigma_3_threshold`, `sigma_applicability`,
  `sigma_decision`, `sigma_flag`, and `sigma_reason`. Both change the
  applicable-method denominator on exactly 100 rows: SRPI, N=50,
  terminal `1_2LT` phase B and terminal `T_MAN` phase C, 50 rows each,
  from four to three. All 204,300 current rows have denominator three.
  Elsewhere, the old sigma method had already been non-applicable.
- Those same tables have recomputed K-Means `score` values differing on
  74,227 rows and `threshold` values differing on 61,000 rows. Maximum
  absolute differences are respectively `4.440892098500626e-16` and
  `2.220446049250313e-16`; maximum relative differences are
  `3.079675386084815e-11` and `2.0805233204750386e-16`. These are small
  floating-point recomputation differences, retained at raw precision;
  no associated flag, applicability, candidate, agreement, reason or
  disagreement changed. They are not attributed to a physical effect.
- `method_comparison.csv` additionally changes `compared_methods` on every
  row to `mad_modified_z;kmeans_distance;dbscan_noise`.
- `convergence.csv` retains 90 rows and changes only `method_policy` to
  `defense-v3-three-methods`; all descriptive measures, empirical
  probabilities, intervals, candidates, rates and deltas remain equal.

Candidate union is **13,716**, and disagreement count is **13,708** in
both versions, established by recomputation and comparison. The retired
detector had zero positive flags in v2; this explains the unchanged union
and agreement, but does not erase the denominator changes. No other common
source-table column differs. Normality rejection remains 88 of 90 groups;
empirical occurrences above 2.3 P.U. remain zero in all 90 groups.

### Reference-group handoff for manuscript correction

The following counts are for terminal `T_OPO`, phase A, separately in each
scenario. Each row's applicable-method denominator is three. All counts
below equal v2 after independent v3 recomputation.

| Scenario | N | Candidate union | MAD | K-Means | DBSCAN | Disagreement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CRPI | 50 | 8 | 8 | 0 | 0 | 8 |
| CRPI | 100 | 12 | 12 | 0 | 1 | 12 |
| CRPI | 200 | 2 | 2 | 1 | 2 | 1 |
| CRPI | 1,000 | 10 | 10 | 9 | 2 | 8 |
| CRPI | 10,000 | 109 | 109 | 99 | 0 | 109 |
| SRPI | 50 | 6 | 6 | 0 | 6 | 6 |
| SRPI | 100 | 12 | 12 | 0 | 0 | 12 |
| SRPI | 200 | 22 | 22 | 1 | 0 | 22 |
| SRPI | 1,000 | 86 | 86 | 9 | 0 | 86 |
| SRPI | 10,000 | 852 | 852 | 99 | 0 | 852 |

T7.5 must remove the old detector's objectives, theory, votes and
interpretations even where resulting candidate counts stay unchanged.
The unchanged zero-event Wilson intervals describe uncertainty under the
model, not independently proven convergence. The unchanged skewness and
kurtosis do not establish a causal explanation for MAD behavior.

Verification details were computed using temporary local scripts, with
machine-readable reconciliation saved to `/tmp/t74-verification.json` for
the sequential handoff. The report preserves all material results without
adding a permanent verification framework. `results/` is ignored by Git;
the generated v3 package remains available locally. Only the validation
report is versioned by this task's commit. Initial staging approval was
aborted; the author subsequently authorized another commit attempt. Manuscript assets, source references,
copying, build and rendered-page review remain T7.5 work.

**SPEC_DEVIATION:** None.

## T7.5 — Correct the manuscript and active guidance

Date: 2026-10-26. Scope: READ-07 only; unrelated editorial tasks remain
pending. T7.4's verified v3 package is the sole current evidence source.

### Scientific claims and publication

- Removed the output-voltage three-sigma objective, theoretical interval
  equation, applicability prescription, fourth comparison vote, results
  comparison, sensitivity explanation and conclusion claims from
  `doc/main.tex`. MAD, K-Means distance and DBSCAN noise remain the three
  applicable criteria; hierarchical labels stay non-voting. The MAD equation,
  descriptive statistics, Gaussian adequacy and qualified probability
  comparison remain unchanged.
- The remaining manuscript references are the symbol for standard deviation
  and the source-model command `SIGMAX=3.0`. The latter is verified at
  `input_files/casos/10000-simulacoes/casos/T_MAN/SRPI/CASO-COMPLETO/SDEF/case.atp:7`,
  with SHA-256
  `0b89b013e7811d473b45896dc815ee1b9df18d50a3b91c50792904b4f14ec0ee`.
  No additional distribution or switching-time parameters were inferred.
- Wilson interval narrowing with zero events is described as reduced
  uncertainty under the interval model, not independent convergence proof.
  The across-N section and captions now describe comparisons. Captions
  identify the two plotted rates rather than claiming unplotted descriptive
  measures. Existing figure-internal metadata/layout remain T10.4 work.
- Removed the unsupported statement that skewness/kurtosis explain MAD's
  sensitivity. They remain descriptive measures; a causal or explanatory
  relationship requires a dedicated analysis.
- Current N=10,000 reference-group counts reconcile to
  `sources/method_comparison.csv`: CRPI MAD/union 109, SRPI MAD/union 852,
  K-Means 99 per scenario and DBSCAN zero per scenario. Across-N source
  reconciliation also corrected the old SRPI rate-range sentence: the
  T_OPO/A rates are 12%, 12%, 11%, 8.6% and 8.52%, so the range is
  8.52%–12% across all five sizes. Neither the old 13.50% upper bound nor
  exclusion of N=1,000 was supported by the current source table.
- All manuscript evidence references point to v3. The unchanged 204,300
  observations, zero exceedances, 88/90 normality rejections, 1,151 reconciled
  ATP bins, benchmark/sensitivity metrics, clustering results and five
  unresolved review records remain supported by the T7.4 table comparison.
  No electrical-review completion or causal ATP-error claim was introduced.
- `uv run python -m scripts.prepare_defense_document` copied all 11 referenced
  tables/figures to `doc/evidence/v3/`. Every copied asset was compared byte
  for byte with its versioned generated source. No v2 reference remains in
  the manuscript. Historical assets and template files were retained.

### Remaining sigma references: classification

The search covered `src/`, `scripts/`, `tests/`, the manuscript, active
guidance, `.notebook/`, `specs/` and `docs/`, alongside T7.4's raw-input and
historical-package hash inventory. References were classified by role,
rather than deleted by matching a word.

| Location | Classification and treatment |
| --- | --- |
| Raw ATP/LIS inputs, including `SIGMAX=3.0`; `.notebook/article-case-comparison.md`; `docs/research/article_case_vs_project_cases.md` | Switching configuration/source comparison. Retained without editing input settings or inferring output Gaussianity. |
| `doc/main.tex` symbol list | Independent descriptive standard deviation. Retained; detector equations removed. |
| `statistics.py`, `distribution_adequacy.py`, plotting callers | Independent descriptive/Gaussian fitting functions remain; retired helpers and caller analysis are documented under T7.2. No voltage-sigma threshold or vote remains. |
| `visualization.py` documentation and regression tests in comparison/pipeline/statistics/evidence builder | Explicit absence/retirement assertions. These references prevent reintroduction, rather than implement a detector. |
| `tests/test_benchmark.py` | Arbitrary method-name labels in generic synthetic metric-aggregation fixtures; no production detector or evidence-generation caller. Retained as isolated test data. |
| `AGENTS.md`, codebase architecture/testing docs, notebook flow/index | Active guidance corrected: three explicit criteria, qualified Gaussian diagnostics and preserved switching parameters. Outdated sigma API descriptions and label-voting notebook claims no longer guide implementation. |
| `atp-data-processing-validation/{spec,design,tasks}.md`, `atp-processamento-validacao/{spec,design,tasks}.md`, `thesis-defense-evidence/spec.md` | Historical requirements explicitly superseded by READ-07 via dated headers. Original requirements, execution facts and results preserved below the notices. |
| Research plans/proposals: `01_tcc_project_plan`, `proposta_tcc_definitivo`, `manual_anomaly_detection_and_test_design`, `defense_validation_plan`, `plano_preparacao_defesa`, `andamento_do_trabalho` | Historical detector instructions receive the same explicit supersession notice; they are not current requirements. |
| Research execution/analysis: `work_progress_summary`, `hierarchical-manuscript-contribution`, `generated_case_plots_analysis` | Historical descriptions receive supersession notices without rewriting the reported old behavior. |
| `data_cleaning_validation_report.md`, `advisor_next_steps_plan.md` | Retained boundary statements: no sigma-based cleaning and no universal Gaussian/sigma inference. They do not prescribe the retired detector. |
| `docs/research/reuniao/transcricao.md` | Verbatim historical meeting evidence. Preserved; the later author decision in READ-07 governs implementation. |
| This validation report, READ-07 spec/tasks and visual-review notes | Explicit correction history, acceptance conditions and regression evidence. Historical statements are dated and not current detector prescriptions. |
| `results/defense-evidence/v1/`, `v2/` and corresponding old `doc/evidence/` assets | Historical evidence retained, not silently overwritten or relabeled. All 3,743 input/historical hashes still match the pre-generation snapshot. |

### Editorial and publication gates

- `just build`: passed; final `doc/build/main.pdf` has 80 physical pages.
  Final log has no undefined references/citations, missing assets,
  overfull/underfull boxes or LaTeX/package warnings. `git diff --check`
  passes. Citation-key and label sets match the pre-edit manuscript.
- Authored manuscript prose is Brazilian Portuguese. Technical commands,
  labels, paths and bibliography keys retain their technical forms. Guidance
  changes and supersession notices are English.
- Rendered changed text pages with Poppler and inspected PNGs at physical
  PDF pages 17, 22, 35, 40–43, 59–60, 65–66 and 71–74 (printed page numbers
  are one less). Checked the final page 65 again after correcting its rate
  range. Changed prose, equations and captions are readable, with no new
  clipping or overlap. Scratch renders remain under `/tmp/t75-render/`.
- Also rendered and inspected the versioned table/figure pages 48–58,
  61–64 and 67–70, in addition to figures 13–14 on page 65. The final
  clustering-introduction version label on page 55 was aligned to v3.
  The root independently spot-checked pages 40 and 65.
- Existing exhaustive landscape tables, whitespace around their page breaks,
  small plot labels and mixed-language figure metadata remain visible
  limitations assigned to T10/T11/T12. This scoped review does not certify
  their later redesign or whole-document final layout.
- No production/test code changed in T7.5; T7.3 owns copier regression tests
  and software gates. The final exact Taskipy gate
  `uv run task test` passed **327 tests**, 0 failed/skipped, in 85.62 s.
  A final orchestrator preservation check again matched all 3,743 hashes.

Initial staging approval for T7.4 was aborted. The author subsequently
authorized another attempt: T7.4 is recorded in commit `3d3d3ce`, and
T7.5 documentation, publication assets and task tracking are recorded
with this manuscript commit. Generated `results/` remain Git-ignored.

**SPEC_DEVIATION:** None in READ-07 behavior or verification. Atomic commit
bookkeeping was completed after the author authorized the retry.
