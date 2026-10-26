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
