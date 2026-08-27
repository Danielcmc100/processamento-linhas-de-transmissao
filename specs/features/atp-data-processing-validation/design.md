# ATP Data Processing and Statistical Validation Design

**Spec:** `specs/features/atp-data-processing-validation/spec.md`
**Status:** Draft

## Architecture overview

```text
Config + input directory
        |
        v
Loader/parser -> normalized observation table
        |
        +--> data-quality validation
        +--> DBSCAN labels
        +--> K-Means labels
        +--> sigma/statistical labels
                    |
                    v
       comparison + terminal summaries
                    |
                    v
     tables + plots + JSON metadata package
```

The implementation should retain the existing service boundaries and add a
small orchestration/reporting layer. It should not introduce a database or
web service.

## Reuse analysis

| Existing component | Location | Reuse |
|---|---|---|
| ATP parser and Pydantic models | `src/parser/` | Extend validation only where fixtures expose gaps |
| Directory loader and P.U. extraction | `src/services/preprocessing.py` | Reuse as the input-table foundation |
| DBSCAN/K-Means primitives | `src/services/clustering.py` | Add validation and stable label semantics |
| Gaussian fit and sigma table | `src/services/statistics.py` | Extend with empirical summaries and guarded variance handling |
| Existing plots | `src/services/visualization.py` | Reuse and make output generation configurable |
| Script orchestration | `main.py` | Extract configuration and reporting seams |

## Components and interfaces

### Analysis configuration

- **Location:** `src/services/pipeline.py` or a dedicated configuration module.
- **Purpose:** Represent input path, encoding, base voltage, terminals, phase
  policy, clustering parameters, threshold, and output directory.
- **Contract:** Configuration is serializable and validates positive voltage,
  supported phase policy, and valid algorithm parameters.

### Data-quality validation

- **Location:** `src/services/validation.py`.
- **Purpose:** Return structured issues and a cleaned observation table.
- **Contract:** Never silently coerce non-finite values; record source file,
  simulation, terminal, and phase whenever available.

### Statistical summary

- **Location:** `src/services/statistics.py`.
- **Purpose:** Add empirical exceedance, sigma status, and guarded Gaussian
  outputs to the existing fit.
- **Contract:** A summary explicitly reports insufficient sample size or zero
  variance instead of producing undefined probabilities.

### Method comparison

- **Location:** `src/services/clustering.py` plus a comparison module if needed.
- **Purpose:** Align DBSCAN, K-Means, and sigma labels by observation identity.
- **Contract:** Output contains algorithm labels, agreement count, and a
  candidate anomaly status; it does not claim physical causation.

### Reproducible runner and artifact writer

- **Location:** `src/services/pipeline.py` and `main.py`.
- **Purpose:** Run all stages and save tables, plots, and metadata.
- **Contract:** No absolute input path; all parameters and counts are persisted.

## Data model

The normalized observation table keeps the current fields:

```text
source_file, simulation, terminal, phase, value_pu, time
```

The analysis table adds:

```text
dbscan_cluster, kmeans_cluster, sigma_flag,
method_agreement, anomaly_candidate, anomaly_reasons
```

The summary table contains per terminal and phase:

```text
n_total, n_valid, n_outliers, mean, std, sigma_3_threshold,
empirical_exceedance, gaussian_exceedance, validation_status
```

Metadata contains configuration, UTC start/end timestamps, Python/package
versions, input file names, file hashes where practical, row counts, and
artifact names.

## Error strategy

| Scenario | Handling |
|---|---|
| Missing directory or no files | Raise a clear configuration/input error |
| Malformed individual file | Record file issue; configurable strict mode decides whether to stop |
| Empty selected terminal/phase | Produce explicit empty status; do not fit |
| Invalid algorithm parameters | Validate before analysis and raise a clear error |
| Zero variance | Mark Gaussian tail as unavailable or deterministic, per documented policy |
| Existing output directory | Require explicit overwrite policy and record it |

## Technical decisions

- Keep DBSCAN per terminal because current code already avoids mixing terminal
  distributions.
- Keep phase selection explicit; default behavior must not silently pool A, B,
  and C.
- Treat outliers as candidate anomalies and preserve them in raw/annotated
  outputs; only filtered data feed a valid-event Gaussian fit.
- Use deterministic K-Means configuration (`random_state`) and persist all
  model parameters.

