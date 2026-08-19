# ATP Data Processing and Statistical Validation Tasks

**Design:** `specs/features/atp-data-processing-validation/design.md`
**Status:** Complete

## Execution plan

### Phase 1 — Evidence and contracts

```text
T1 -> T2 -> T3
```

### Phase 2 — Analysis services

```text
             +-> T4 ->+
T3 ----------+         +-> T6 -> T7
             +-> T5 ->+
```

### Phase 3 — Integration and evidence

```text
T7 -> T8 -> T9
```

## Task breakdown

### T1: Add representative parser and loader fixtures [Complete]

- **Requirement:** ATP-01, ATP-02, ATP-03
- **Where:** `tests/fixtures/`, parser and preprocessing tests
- **Depends on:** None
- **Done when:** Fixtures cover multiple runs, phases, terminals, negative
  values, and at least one malformed/empty input policy; expected rows and
  normalized values are asserted.
- **Tests:** Unit tests, co-located.
- **Gate:** `uv run pytest tests/test_parser.py tests/test_preprocessing.py`

### T2: Define validated analysis configuration [Complete]

- **Requirement:** ATP-07
- **Where:** `src/services/pipeline.py` or configuration module and tests
- **Depends on:** T1
- **Done when:** Configuration validates paths, base voltage, phase policy,
  terminals, DBSCAN/K-Means parameters, threshold, and output policy; it is
  serializable.
- **Tests:** Unit tests for valid and invalid configurations.
- **Gate:** `uv run ruff check . && uv run pytest`

### T3: Add structured data-quality validation [Complete]

- **Requirement:** ATP-03
- **Where:** `src/services/validation.py` and tests
- **Depends on:** T1, T2
- **Done when:** Non-finite values, missing selections, inconsistent inputs,
  and empty datasets produce structured, testable statuses.
- **Tests:** Unit tests for each edge-case policy.
- **Gate:** `uv run ruff check . && uv run pytest`

### T4: Extend empirical and guarded statistical summaries [Complete]

- **Requirement:** ATP-04
- **Where:** `src/services/statistics.py`, `tests/test_statistics.py`
- **Depends on:** T3
- **Done when:** Per-terminal summaries include empirical exceedance, Gaussian
  exceedance, sigma thresholds, and explicit insufficient/zero-variance
  statuses.
- **Tests:** Unit tests with deterministic values and edge cases.
- **Gate:** `uv run ruff check . && uv run pytest tests/test_statistics.py`

### T5: Harden DBSCAN and integrate tested K-Means labels [Complete]

- **Requirement:** ATP-05
- **Where:** `src/services/clustering.py`, `tests/test_clustering.py`
- **Depends on:** T3
- **Done when:** Empty/small/invalid inputs are guarded, labels preserve row
  identity, and both algorithms have deterministic tests.
- **Tests:** Unit tests for separated clusters, noise, and invalid parameters.
- **Gate:** `uv run ruff check . && uv run pytest tests/test_clustering.py`

### T6: Implement statistical-versus-clustering comparison [Complete]

- **Requirement:** ATP-06
- **Where:** `src/services/comparison.py`, `tests/test_comparison.py`
- **Depends on:** T3, T4, T5
- **Done when:** Every observation has method labels, agreement count,
  candidate status, and reasons; physical causation is not asserted.
- **Tests:** Unit tests for agreement, disagreement, and missing method labels.
- **Gate:** `uv run ruff check . && uv run pytest tests/test_comparison.py`

### T7: Build the configurable end-to-end runner [Complete]

- **Requirement:** ATP-07
- **Where:** `src/services/pipeline.py`, `main.py`, integration tests
- **Depends on:** T2, T3, T4, T5, T6
- **Done when:** A fixture directory runs through loading, analysis,
  comparison, and plotting without a hard-coded machine path.
- **Tests:** Integration test with temporary input/output directories.
- **Gate:** `uv run ruff check . && uv run pytest`

### T8: Write auditable result artifacts [Complete]

- **Requirement:** ATP-08
- **Where:** pipeline/report writer and integration tests
- **Depends on:** T7
- **Done when:** Raw/annotated data, summary tables, figures, configuration,
  counts, and runtime metadata are saved and re-runnable.
- **Tests:** Artifact existence, schema, deterministic contents, and overwrite
  policy tests.
- **Gate:** `uv run ruff check . && uv run pytest`

### T9: Repair type-checking and document validation evidence [Complete]

- **Requirement:** ATP-08, ATP-09
- **Where:** `src/services/visualization.py`, project state, TCC notes
- **Depends on:** T8
- **Done when:** BasedPyright passes, limitations are documented, and the
  evidence package is referenced by the TCC workflow.
- **Tests:** Full quality gate.
- **Gate:** `uv run ruff check . && uv run ruff format --check . && uv run basedpyright && uv run pytest`

## Traceability matrix

| Requirement | Tasks | Coverage |
|---|---|---|
| ATP-01 | T1 | Complete |
| ATP-02 | T1 | Complete |
| ATP-03 | T1, T3 | Complete |
| ATP-04 | T4 | Complete |
| ATP-05 | T5 | Complete |
| ATP-06 | T6 | Complete |
| ATP-07 | T2, T7 | Complete |
| ATP-08 | T8, T9 | Complete |
| ATP-09 | T9 | Complete |

## Pre-approval checks

### Granularity

Each task has one primary deliverable, one code boundary, and co-located tests
where code is added or changed. **Pass.**

### Dependency cross-check

| Task | Declared dependencies | Diagram predecessor(s) | Result |
|---|---|---|---|
| T1 | None | None | Pass |
| T2 | T1 | T1 | Pass |
| T3 | T1, T2 | T2 | Pass |
| T4 | T3 | T3 | Pass |
| T5 | T3 | T3 | Pass |
| T6 | T3, T4, T5 | T3, T4, T5 | Pass |
| T7 | T2, T3, T4, T5, T6 | T6 | Pass |
| T8 | T7 | T7 | Pass |
| T9 | T8 | T8 | Pass |

### Test co-location

| Task | Required test type | Tests included | Result |
|---|---|---|---|
| T1 | Unit | Yes | Pass |
| T2 | Unit | Yes | Pass |
| T3 | Unit | Yes | Pass |
| T4 | Unit | Yes | Pass |
| T5 | Unit | Yes | Pass |
| T6 | Unit | Yes | Pass |
| T7 | Integration | Yes | Pass |
| T8 | Integration | Yes | Pass |
| T9 | Full gate | Yes | Pass |
