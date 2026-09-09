# ATP Data Processing and Statistical Validation Specification

**Status:** Complete — implemented and verified with synthetic fixtures and
real ATP statistical files within the documented supported layout scope
**Source:** TCC objectives in `doc/main.tex`, repository inspection on
2026-08-14

## Problem statement

The project has isolated processing components, but it does not yet prove that
the complete ATP analysis is reproducible on representative data or that an
outlier classification is supported by both statistical and clustering
evidence. The feature closes that gap while preserving the TCC boundary: it
produces auditable analytical evidence, not an automated insulation decision.

## Objective completion assessment

| Objective | Current evidence | Assessment |
|---|---|---|
| Extract raw ATP statistical data | Parser, loader, fixtures, and real-file audit | **Implemented and accepted for the audited ATP layouts** |
| Structure data for phase maxima | Typed models, Polars extraction, and tests | **Implemented and verified for the supported schema** |
| Preprocess and apply `3sigma` criteria | P.U. normalization, validation, and guarded summaries | **Implemented and fixture-verified; normality validation pending** |
| Probabilistic overvoltage analysis | Empirical/Gaussian exceedance summaries and plots | **Implemented and fixture-verified; no confidence intervals or goodness-of-fit test** |
| Apply K-Means and DBSCAN | Both methods are integrated with deterministic tests | **Implemented and fixture-verified; parameters require target-data validation** |
| Compare statistical and clustering results | Row-aligned labels, agreement, status, and reasons | **Implemented and fixture-verified as candidate evidence only** |
| Reproducible integrated routine | Validated JSON CLI, integration tests, and seven artifacts | **Implemented and fixture-verified** |

## Goals

- [x] Validate the parser and loader using synthetic fixtures and independently
  checked records from representative real ATP `.lis` files.
- [x] Make the analysis inputs and model parameters explicit and reproducible.
- [x] Produce empirical and Gaussian probability evidence with documented
  assumptions.
- [x] Integrate and test K-Means and DBSCAN where method comparison is needed.
- [x] Classify anomalies as analytical candidates with traceable reasons,
  without claiming that clustering proves a numerical ATP failure.
- [x] Generate an auditable result package containing tables, figures, and
  metadata.

## Out of scope

| Item | Reason |
|---|---|
| Automated insulation optimization | Explicitly excluded from the TCC |
| Expert-system recommendation | Protected company intellectual property |
| Physical ATP simulation generation | This feature consumes ATP outputs |
| Automatic assertion that every DBSCAN noise point is a numerical error | Requires domain validation beyond unsupervised learning |

## User stories and acceptance criteria

### P1: Parse and normalize an analysis dataset

As a researcher, I want a directory of ATP outputs converted into a typed,
normalized table so that every analyzed observation can be traced to a
simulation, terminal, phase, value, and time.

1. WHEN valid `.lis` files are supplied THEN the system SHALL parse all
   supported runs and aggregate phase-to-ground maxima.
2. WHEN a base voltage and terminal set are supplied THEN the system SHALL
   normalize values to P.U. and preserve the source identifiers.
3. WHEN a file is empty, malformed, or has no selected terminal THEN the system
   SHALL report or skip it according to a documented policy and SHALL NOT
   silently fabricate observations.

**Independent test:** Run the loader over committed fixtures and compare row
counts, fields, and normalized values with expected outputs.

### P1: Produce statistical and probabilistic evidence

As a researcher, I want per-terminal summaries that combine empirical and
Gaussian analysis so that extreme values can be discussed with quantified
uncertainty and assumptions.

1. WHEN a terminal has valid observations THEN the system SHALL report count,
   mean, sample standard deviation, sigma thresholds, and Gaussian tail
   probabilities.
2. WHEN a threshold such as 2.3 P.U. is supplied THEN the system SHALL report
   both empirical exceedance and fitted-Gaussian exceedance where estimable.
3. WHEN a terminal has insufficient or zero variance data THEN the system SHALL
   return a documented validation result instead of an invalid tail estimate.

**Independent test:** Use deterministic fixtures with known values and verify
the summary and exceedance calculations.

### P1: Detect and compare candidate anomalies

As a researcher, I want DBSCAN, K-Means, and sigma-based labels compared in one
result table so that an outlier is not interpreted from one method alone.

1. WHEN clustering parameters are supplied THEN the system SHALL record the
   algorithm, parameters, cluster label, and source row for every observation.
2. WHEN an observation is flagged by one or more methods THEN the system SHALL
   expose the method agreement/disagreement and a non-conclusive candidate
   anomaly status.
3. WHEN K-Means is requested with invalid cluster count or insufficient rows
   THEN the system SHALL fail with a clear validation error.

**Independent test:** Use synthetic separated clusters and known extreme
points to verify labels, agreement columns, and invalid-input handling.

### P1: Execute a reproducible analysis run

As a researcher, I want one configurable command to run the pipeline and save
results so that figures and tables used in the TCC can be regenerated.

1. WHEN a configuration specifies input path, phase policy, voltage base,
   terminals, algorithm parameters, and output directory THEN the system SHALL
   run without machine-specific paths.
2. WHEN the run completes THEN the system SHALL save analytical tables,
   figures, parameters, counts, and software/runtime metadata.
3. WHEN a required input or configuration is invalid THEN the system SHALL
   fail before producing a misleading result package.

**Independent test:** Run the same fixture and configuration twice and compare
the deterministic tables and metadata fields that are expected to be stable.

## Edge cases

- Empty directory or no matching `.lis` files.
- Missing `NENERG`, missing headers, truncated run, or inconsistent value/time
  counts.
- Negative voltage maxima and non-finite values.
- One observation, fewer observations than `min_samples`, or zero variance.
- Multiple phases with materially different distributions.
- Terminal names not present in the input.
- Re-running into an existing output directory.

## Requirement traceability

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| ATP-01 | Parse and aggregate supported `.lis` files | P1 | Verified on audited real ATP layouts |
| ATP-02 | Normalize and preserve traceable observation fields | P1 | Implemented and verified |
| ATP-03 | Validate data quality and edge cases | P1 | Implemented and verified |
| ATP-04 | Produce Gaussian, sigma, and empirical probability summaries | P1 | Implemented and verified |
| ATP-05 | Run and record DBSCAN and K-Means classifications | P1 | Implemented and verified |
| ATP-06 | Compare statistical and clustering evidence | P1 | Implemented and verified |
| ATP-07 | Execute a configurable reproducible pipeline | P1 | Implemented and verified |
| ATP-08 | Save auditable tables, figures, and metadata | P1 | Implemented and verified |
| ATP-09 | Preserve TCC scope boundary | P1 | Verified |

**Coverage:** 9 total; 9 implemented and mapped to completed tasks. Real-data
and domain validation remain research activities rather than implementation
gaps.

## Success criteria

- All committed gates pass, including BasedPyright.
- A representative fixture completes end to end with deterministic row counts
  and result artifacts.
- Every anomaly in the report has statistical and clustering evidence recorded.
- The generated package can be regenerated from its configuration without a
  machine-specific path.

These criteria are verified with synthetic fixtures and the real-file parser
audit. They do not prove the physical or numerical cause of an anomaly.
