# ATP Analysis Validation Evidence

**Validation date:** 2026-08-18

## Scope of the evidence

The committed end-to-end fixture, `tests/fixtures/representative.lis`, is a
representative **synthetic** ATP-like dataset. It exercises the supported
parser structure, terminals, phases, normalization, validation, clustering,
statistics, plots, and artifact writer. It is not a real company ATP dataset.
Validation with representative real ATP outputs and review of the resulting
models by the electrical-engineering domain remain pending.

One explicit phase (`A`, `B`, or `C`) is analyzed per run. This avoids silently
pooling phase distributions and makes the selected phase part of the saved
configuration.

## Reproducible command workflow

Create a JSON file accepted by `AnalysisConfig`. Paths may be relative to the
working directory; no machine-specific path is required. For example:

```json
{
  "input_path": "tests/fixtures",
  "encoding": "iso-8859-1",
  "base_voltage": 100000.0,
  "terminals": ["T_MAN", "T_OPO"],
  "phase_policy": "A",
  "dbscan": {"eps": 3.0, "min_samples": 2},
  "kmeans": {"n_clusters": 2, "random_state": 42},
  "threshold": 3.0,
  "output_dir": "results/representative-a",
  "overwrite": false
}
```

Run the package from the repository root:

```console
uv run python main.py analysis-config.json
```

The generated `configuration.json` records the complete validated input and
model configuration. To regenerate the package, pass that file to the same
command. When `overwrite` is `false`, generation stops before writing if any
of the seven known artifacts already exists. Choose a new output directory or
explicitly set `overwrite` to `true`. With overwrite enabled, only the seven
known artifacts are replaced; unrelated files in the output directory are
preserved. The runtime timestamp in metadata is intentionally different on
each run, while tables and the remaining configuration content are tested for
determinism.

## Result package

Every successful run writes exactly these seven artifacts:

1. `raw_observations.csv` — parsed and normalized traceable observations.
2. `annotated_observations.csv` — method labels, agreement, candidate status,
   and reasons for analyzed observations.
3. `summary.csv` — per-terminal and phase statistical summaries.
4. `configuration.json` — validated parameters needed to repeat the run.
5. `metadata.json` — artifact names, row counts, input hashes, UTC generation
   time, and software versions.
6. `combined.png` — observations and fitted Gaussian PDF overlays.
7. `exceedance.png` — empirical and fitted-Gaussian exceedance curves.

## Quality-gate evidence

The complete repository gate was executed in the required order on
2026-08-18:

```console
uv run task format
uv run task lint
uv run ruff format --check .
uv run basedpyright
uv run task test
```

All commands passed. BasedPyright reported zero errors, warnings, and notes.
Pytest reported **91 passed, 0 skipped**; no tests were deleted for this
validation.

## Interpretation limits

The current software reports empirical exceedance, a fitted-Gaussian
exceedance, sample mean and standard deviation, and a three-sigma threshold.
It does not yet perform a normality or goodness-of-fit test and does not
calculate confidence intervals. Gaussian results therefore remain
model-dependent descriptive evidence, not proof that the target population is
normally distributed.

DBSCAN noise labels and membership in the K-Means cluster with the highest
centroid are candidate anomaly evidence. The K-Means meaning is an explicit
semantic heuristic, not an intrinsic property of the algorithm. Agreement
among DBSCAN, K-Means, and sigma flags strengthens an analytical candidate but
does not prove an ATP numerical error or establish a physical cause. Those
conclusions require validation on real outputs and engineering review.

The package supports extraction, preprocessing, statistical description,
candidate comparison, and reproducible evidence generation. It does not
optimize insulation levels and does not implement an expert system or an
automated engineering decision.
