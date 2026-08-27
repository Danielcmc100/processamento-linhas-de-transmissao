# Architecture

**Pattern:** Layered, library-first Python application with a thin script
orchestrator.

## Data flow

```text
ATP .lis files
    -> src.parser.parse_statistical_data
    -> Pydantic parser models
    -> preprocessing.extract_maxima_dataframe / load_directory
    -> Polars DataFrame in P.U.
    -> clustering and filtering
    -> Gaussian statistics and exceedance probabilities
    -> Matplotlib figures and console output
```

## Modules

- `src/parser/`: regular-expression parsing and Pydantic models for `.lis`
  sections and simulation runs.
- `src/services/preprocessing.py`: file loading, phase-to-ground filtering,
  terminal extraction, and P.U. normalization.
- `src/services/clustering.py`: standardized one-dimensional DBSCAN and
  K-Means operations plus valid-event filtering.
- `src/services/statistics.py`: Gaussian fit result and sigma/probability
  calculations.
- `src/services/visualization.py`: scatter, Gaussian overlay, and empirical
  versus fitted exceedance plots.
- `main.py`: fixed-configuration end-to-end orchestration.

## Observed integration boundary

The services exchange Polars DataFrames with stable columns such as
`terminal`, `phase`, and `value_pu`. The script currently owns configuration,
logging, fitting, and output persistence, which makes it the main seam for the
next reproducibility increment.

