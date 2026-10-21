# Main Research Objective Summary

The main objective stated in `doc/main.tex` is to develop a computational
model that automates the extraction, statistical treatment, probabilistic
analysis, and classification of ATP simulation data. The model focuses on
identifying anomalies and extreme overvoltage values produced during the
energization of transmission lines.

For the thesis defense, the intended contribution should be presented as a
reproducible decision-support workflow. It organizes large ATP result sets,
combines statistical criteria with unsupervised learning, and flags values
that require technical investigation. It does not replace electrical
engineering judgment, automatically discard anomalous observations, prove
their physical cause, or make the final insulation-coordination decision.

Source: `doc/main.tex`, Introduction and Objectives sections.

## Meaning of Extreme Values and Anomalies

The manuscript defines an extreme value as an observation located far from
the central region of its statistical distribution. Preliminary candidate
criteria include values outside mean plus or minus three standard deviations,
values outside the 1.5-IQR boxplot limits, and values exceeding an explicitly
selected overvoltage threshold.

An anomaly is defined more broadly as a maximum overvoltage that differs
significantly from the predominant behavior of comparable ATP simulations.
Statistical rules and clustering provide analytical evidence: distance from a
K-Means centroid or a low-density DBSCAN noise label may identify a candidate.
Neither condition proves that the observation is an ATP numerical error.

The operational definition remains incomplete in the manuscript. Grouping
keys, input features, scaling, thresholds, and evaluation rules are still
marked for development. The correction specification also leaves K-Means
threshold selection and DBSCAN calibration for the design phase because no
reviewed ground-truth anomaly labels exist. Final physical-versus-numerical
classification requires inspection of the source case, switching parameters,
other terminals and phases, and, when necessary, waveform evidence.

Sources: `doc/main.tex`, Statistical Analysis, Anomaly Detection, Clustering,
and Results Limitations sections; `specs/features/clustering-anomaly-correction/spec.md`.

The decision-support role and exclusions are now stated explicitly in the
Portuguese summary, English abstract, and the Introduction section titled
"Escopo e limites da proposta".
