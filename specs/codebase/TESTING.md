# Testing and Verification

## Current tests

- `tests/test_parser.py`: parser behavior for a synthetic two-run `.lis`
  block.
- `tests/test_preprocessing.py`: phase-to-ground filtering, P.U.
  normalization, and terminal selection.
- `tests/test_statistics.py`: descriptive Gaussian fits, tail probabilities,
  sigma-free summary contracts, and empty/non-finite/zero-variance behavior.
- `tests/test_visualization.py`: Matplotlib smoke tests and terminal coverage.

Historical result on 2026-08-14: **17 tests passed** with `uv run pytest`.
READ-07 verification on 2026-10-26: **327 tests passed**; current detailed
gates and caller classification are recorded in
`docs/research/thesis_sigma_correction_validation.md`. Historical sigma
screening tests were replaced with the three-method and sigma-free output
contracts; Gaussian adequacy and descriptive-statistics tests remain.

## Quality gates

```text
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pytest
```

The 2026-08-14 mapping reported six BasedPyright errors in
`src/services/visualization.py`; READ-07's recorded gate passes with zero
errors. New code should include unit tests in the
same task and add integration tests whenever it crosses parser, preprocessing,
analysis, and output boundaries.

