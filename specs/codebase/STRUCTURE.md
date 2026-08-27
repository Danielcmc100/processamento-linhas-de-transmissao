# Project Structure

```text
src/parser/       ATP `.lis` parsing and domain models
src/services/     preprocessing, statistics, clustering, visualization
tests/             unit and smoke tests
doc/               TCC manuscript, plan, bibliography, images
main.py            current end-to-end script
pyproject.toml     dependencies, quality gates, Taskipy commands
```

The repository is organized by technical layer rather than by user-facing
feature. The TCC manuscript and implementation are kept in the same project,
but there is currently no committed dataset or generated-results directory.

