# Code Conventions

- Functions and variables use `snake_case`; classes use `PascalCase`.
- Public functions have Google-style English docstrings and type hints.
- Strings use double quotes and lines are limited to 79 characters.
- Imports are grouped and checked by Ruff.
- Polars is used for tabular transformations; Pydantic is used for parsed
  domain records.
- Tests are colocated under `tests/` and use small synthetic fixtures.
- Existing implementation uses explicit exceptions for empty statistical
  inputs and returns empty DataFrames with declared schemas for empty data.

