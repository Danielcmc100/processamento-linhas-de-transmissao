# Manual anomaly detection and controlled test design

Date: 2026-09-11

## Scope and interpretation

The current thesis describes peak magnitudes and their occurrence times,
not complete waveforms. These features support statistical screening but
cannot establish oscillation frequency, duration, or numerical causation.
An outlier is a candidate for investigation, not a confirmed ATP error.
Accepted parsing and P.U. conversion do not establish physical validity.

## Manual review protocol

1. Compare observations from comparable scenarios, terminals, and phases.
   Keep SRPI and CRPI separate initially. Preserve source and run identity.
2. Inspect sorted peaks, scatter plots, histograms, and box plots. Use
   quartile fences or a justified statistical criterion to flag candidates.
   Gaussian three-sigma limits require checking distribution suitability;
   peak distributions are not automatically Gaussian.
3. Check the original LIS entry, units, voltage reference, sign convention,
   occurrence time, and observation identity. A negative signed peak is not
   itself invalid: the current analysis uses its magnitude.
4. Compare phases and terminals within the same run, considering switching
   conditions. Phase asymmetry alone does not establish an error.
5. Recover waveforms where possible. Examine the peak neighborhood and
   switching events; sharp changes can be physically meaningful.
6. For numerical investigation, rerun the same realized switching times,
   model, and initial conditions at successively smaller integration steps
   (for example, dt, dt/2, dt/4). Preserve sufficient output resolution.
   Compare peak magnitude, timing, and waveform behavior using a predefined
   engineering tolerance. Sensitivity is evidence for further investigation;
   convergence alone does not validate the physical model.
7. Record source, evidence, reviewer, and conclusion: data defect, suspected
   numerical artifact, physically plausible extreme, or unresolved case.

## Controlled experiments

The following are proposed experiments, not experiments executed here.
Use copies and retain unchanged source data.

| Family | Example intervention | What the test establishes |
| --- | --- | --- |
| Integrity | NaN, missing/duplicate key, time outside [0, 0.3] s for the current cases | Cleaning and validation behavior |
| Point contamination | Multiply selected peaks by 1.2, 1.5, or 2; also inject downward shifts | Sensitivity to known artificial perturbations |
| Contextual contamination | Replace a peak with one plausible globally but unusual for its terminal/scenario | Detection conditional on context |
| Collective contamination | Shift a small subset of runs together | Sensitivity to anomalous groups that may form clusters |
| Physical scenario | Vary permitted closing times or pole spread within the model's scope | Response to valid physical variation; extremes must not be labeled errors automatically |
| Numerical sensitivity | Compare integration steps with identical physical inputs | Evidence of discretization sensitivity; no guaranteed artifact generation |

Do not describe spreadsheet or CSV injections as ATP-generated numerical
errors. Their labels establish intervention provenance, not physical cause.
Do not modify every value uniformly and expect within-dataset clustering to
detect a common scaling error: that requires an external reference check.
Waveform spikes or oscillations require waveform data; a peak-only table
cannot test their temporal characteristics.

## Evaluation design

Start with reviewed baseline runs; retain unresolved baseline cases as
unresolved. Create independent copies with, for example, 1%, 5%, and 10%
contamination and multiple fixed random seeds. Define whether contamination
is counted per row or per run. Store original and injected values, affected
keys, intervention family, intensity, and seed in a separate manifest.

Split by run (and source lineage where runs recur across files), keeping all
phases and terminals of a run together. Fit scaling and choose thresholds
on development data only. Evaluate on held-out runs and perturbations.
Compare three-sigma screening where justified, a robust baseline such as
IQR/MAD, DBSCAN, and K-Means with an explicit distance-based anomaly rule.
Report precision, recall, F1, and false-positive rate on reviewed baseline
data, by intervention family and intensity. Report integrity rejection
separately from statistical anomaly detection. Keep physical extremes in
the evaluation to assess mistaken error classification. Synthetic success
supports detection of the tested perturbations, not proof of ATP error
diagnosis. Mild injections need not become statistically distinguishable.

The thesis already records duplicate, missing-row, NaN, and out-of-window
tests in its data-cleaning validation subsection. Those tests validate
integrity handling, not the later statistical detector.

## Sources

- NIST, Detection of Outliers:
  https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
  Discusses distribution assumptions and masking/swamping.
- NIST, What are outliers in the data?:
  https://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm
  Supports graphical screening and quartile-based fences.
- PSCAD, Simulation settings:
  https://www.pscad.com/webhelp/PSCAD/Application_Project_and_Workspace_Options/Project_Settings/Network.htm
  Documents numerical chatter in EMTDC. This is an illustrative EMT source,
  not evidence that the current ATP cases contain that artifact or that
  PSCAD-specific settings apply to ATP.

The experimental protocol above is a proposed design for this project;
it is not a procedure claimed verbatim from these references.
