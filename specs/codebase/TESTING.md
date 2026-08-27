# Testing and Verification

## Current tests

- `tests/test_parser.py`: parser behavior for a synthetic two-run `.lis`
  block.
- `tests/test_preprocessing.py`: phase-to-ground filtering, P.U.
  normalization, and terminal selection.
- `tests/test_statistics.py`: Gaussian means, sigma levels, tail
  probabilities, and empty-input behavior.
- `tests/test_visualization.py`: Matplotlib smoke tests and terminal coverage.

Current result on 2026-08-14: **17 tests passed** with `uv run pytest`.

## Quality gates

```text
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pytest
```

Ruff checks pass. BasedPyright currently fails with six errors in
`src/services/visualization.py`. New code should include unit tests in the
same task and add integration tests whenever it crosses parser, preprocessing,
analysis, and output boundaries.

