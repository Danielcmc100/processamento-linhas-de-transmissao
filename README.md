# Processamento de Dados em Linhas de Transmissão

## Running the analysis

### Install the project

The project requires Python 3.13 or newer and
[`uv`](https://docs.astral.sh/uv/). Install the locked dependencies from the
repository root:

```bash
uv sync
```

### Create the analysis configuration

Create an `analysis-config.json` file. The input directory must already exist;
the output directory is created automatically when necessary.

```json
{
  "input_path": "tests/fixtures",
  "schema_version": "1.0.0",
  "generator_version": "1.0.0",
  "encoding": "iso-8859-1",
  "base_voltage": 112677.0,
  "scenario": "SRPI",
  "sample_size": 2,
  "source_lineage": "representative-srpi-2",
  "event_definition": "absolute_phase_to_ground_maximum",
  "terminals": ["T_MAN", "T_OPO"],
  "phase_policy": "A",
  "dbscan": {
    "eps": 3.0,
    "min_samples": 2
  },
  "kmeans": {
    "n_clusters": 2,
    "random_state": 42
  },
  "hierarchical": {
    "min_gap_pu": 0.05,
    "gap_factor": 5.0,
    "max_tail_fraction": 0.1
  },
  "threshold": 2.3,
  "output_dir": "results/representative-a",
  "overwrite": false
}
```

The main parameters are:

- `input_path`: directory searched recursively for ATP `.lis` files.
- `base_voltage`: voltage base in volts used for P.U. normalization.
  For the validated 138 kV SRPI/CRPI cases, use **112677.0 V**, matching
  the ATP phase-to-ground peak reference. See
  [the thesis justification](doc/main.tex).
- `terminals`: terminal names without the phase suffix (`A`, `B`, or `C`).
- `phase_policy`: the single phase analyzed in this run.
- `dbscan`: DBSCAN neighborhood and minimum-sample parameters.
- `kmeans`: number of clusters and deterministic random seed. The number of
  clusters is checked against each comparable calibration group; groups
  with insufficient observations yield non-applicable K-Means evidence.
- `hierarchical`: minimum adjacent voltage gap in P.U., multiplier of the
  median adjacent gap, and maximum fraction in the separated upper tail.
  Omission preserves the shown defaults for older input files.
- `threshold`: P.U. value used for empirical and Gaussian exceedance results.
- `output_dir`: directory that receives the result package.
- `overwrite`: when `false`, the run stops before replacing an existing result
  artifact; when `true`, only known result artifacts are replaced.

### Execute the pipeline

Run the command from the repository root:

```bash
uv run python main.py analysis-config.json
```

Each successful run writes the following files to `output_dir`:

- `raw_observations.csv`
- `annotated_observations.csv`
- `summary.csv`
- `configuration.json`
- `metadata.json`
- `combined.png`
- `exceedance.png`
- `overvoltage_histogram.png`
- `switching_time.png`

The saved `configuration.json` can be passed to the same command to reproduce
the analysis. Select a new output directory or set `overwrite` to `true` when
regenerating an existing package.

## Thesis compilation

[`doc/`](doc/) contains only the standalone thesis build sources, local
figures and tables, preserved template assets, bibliography and UFPA style files.
Research notes, audit evidence and reference material live under [`docs/`](docs/).

```sh
just build
```

Output: `doc/build/main.pdf`. System dependencies are listed in
[`justfile`](justfile). See [`docs/README.md`](docs/README.md) for
installation, build commands and evidence regeneration. Compilation does
not require Python, ATP inputs or files outside `doc/`.
