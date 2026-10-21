# Defense Validation Plan

## Validation question

The thesis should validate whether the application produces correct,
reproducible, stable, and technically interpretable analytical evidence from
the declared ATP datasets. It should not claim automatic identification of an
ATP numerical error without reviewed electrical or waveform evidence.

## Current evidence and blockers

The parser, observation identity, completeness, P.U. conversion, cleaning,
and reproducibility controls already have documented evidence. The final
statistical and clustering conclusions remain unvalidated.

Two blockers must be resolved before final-result validation:

1. Regenerate final result packages with the accepted 112677 V base. Saved
   packages based on 100000 V cannot support final threshold conclusions.
2. Correct clustering semantics. Highest-centroid K-Means membership is not
   anomaly evidence, and the current DBSCAN configuration is inert on target
   data.

## Validation matrix

| Claim | Validation procedure | Evidence |
|---|---|---|
| ATP data were extracted correctly | Compare independently transcribed source checkpoints, declared run counts, and row keys | Existing parser and observation audit reports |
| P.U. values are correct | Recalculate checkpoints independently and reconcile ATP summaries | Existing P.U. validation report |
| Probability estimates are correct | Compare direct counts, ATP table frequencies, and exceedance columns; record boundary rules | Count reconciliation table |
| Gaussian inference is adequate | Inspect histogram and Q-Q plot; report skewness, tail behavior, and a documented goodness-of-fit diagnostic | Distribution adequacy table and plots |
| Results do not depend excessively on sample size | Compare 50, 100, 200, 1,000, and 10,000 runs using the same scenario and base | Cross-sample convergence table |
| Anomaly logic detects defined perturbations | Inject traceable point, contextual, and collective perturbations into copies | Precision, recall, F1, and false-positive rate by perturbation |
| Normal high-voltage groups are preserved | Test two dense valid clusters plus isolated distant points | Synthetic regression result |
| Detector behavior is stable | Repeat random initialization and threshold or parameter sensitivity analysis | Candidate-rate and candidate-set stability table |
| Candidates are technically interpretable | Review selected candidates against source rows, terminals, phases, switching conditions, and available waveforms | Signed review sheet with conclusions and unresolved cases |
| Final package is reproducible | Rerun saved configuration from unchanged hashed inputs and compare deterministic artifacts | Hashes, versions, commands, and artifact comparison |

## Recommended experiments

### 1. Probability and distribution validation

Use empirical exceedance as the primary result. For each terminal and phase,
report occurrence count, sample count, probability, and a binomial confidence
interval for relevant thresholds. Compare direct observation counts with ATP
frequency and exceedance tables when both are available.

Do not assume Gaussian adequacy from the use of switching-time distributions.
Compare empirical and Gaussian exceedance estimates, especially in the upper
tail. If diagnostics reject or question the approximation, retain the
Gaussian curve as a comparison and qualify inferential claims.

### 2. Sample-size convergence

For 50, 100, 200, 1,000, and 10,000 simulations, use identical scenario,
phase, terminal, base voltage, and event definitions. Compare:

- mean, standard deviation, median, and selected percentiles;
- empirical exceedance at declared thresholds;
- confidence-interval width;
- fitted thresholds and anomaly candidate rates;
- candidate diagnostics by terminal and phase.

Treat stabilization as evidence of sampling consistency, not detection
accuracy. Disclose whether datasets are nested or independently generated.

### 3. Controlled anomaly experiments

Preserve original files and inject anomalies only into copied datasets. Use
fixed seeds and store an injection manifest containing source key, original
value, injected value, intervention, intensity, and seed. Evaluate at several
contamination rates and intensities.

Include point, contextual, and collective perturbations. Split development
and evaluation data by simulation run, keeping terminals and phases from one
run together. Fit scaling and thresholds on development data only.

Compare three-sigma screening when distributionally justified, IQR or MAD as
a robust baseline, corrected K-Means distance evidence, and calibrated DBSCAN
noise evidence. Synthetic labels validate detection of the injected
intervention, not diagnosis of a real ATP numerical error.

### 4. Stability and sensitivity

Repeat K-Means across fixed documented seeds. Vary K-Means cluster count,
distance threshold policy, DBSCAN parameters or calibration, and statistical
cutoffs within justified ranges. Report how candidate counts and identities
change. A useful detector should not classify an entire ordinary upper-voltage
cluster as anomalous and should not change radically under small reasonable
parameter variations.

### 5. Technical review

Select candidates representing agreement, disagreement, and no-flag cases.
Review source identity, original LIS value, time, terminal, phase, other phases
and terminals in the same run, and switching conditions. Where possible,
inspect waveforms and rerun identical switching conditions with smaller
integration steps. Record each conclusion as data defect, suspected numerical
artifact, physically plausible extreme, or unresolved.

## Minimum defense package

1. One cross-sample table for 50 through 10,000 simulations.
2. One empirical-versus-Gaussian exceedance plot with adequacy qualification.
3. One controlled-injection benchmark table with precision, recall, F1, and
   false-positive rate.
4. One method-comparison table for statistical, robust, K-Means, and DBSCAN
   evidence.
5. One parameter-sensitivity or stability plot.
6. One technical-review table containing representative candidates and
   unresolved cases.
7. One reproducibility manifest with input hashes, configuration, code
   revision, package versions, commands, and generated artifact hashes.

## Acceptance language

Accept final results only within the tested scenarios, terminals, phases,
sample sizes, and parameter policies. State separately whether each result
validates software correctness, statistical adequacy, detector behavior, or
electrical interpretation. Never use software-test success as evidence of a
candidate's physical or numerical cause.

