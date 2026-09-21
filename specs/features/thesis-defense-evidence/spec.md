# Thesis Defense Evidence Package Specification

**Status:** Draft
**Complexity:** Complex
**Source:** `doc/defense_validation_plan.md`
**Primary manuscript:** `doc/main.tex`
**Related features:**

- `specs/features/atp-data-processing-validation/spec.md`
- `specs/features/atp-statistical-probability/spec.md`

## Problem statement

The thesis already documents accepted evidence for ATP parsing, observation
identity, P.U. conversion, and data cleaning. It does not yet provide a final,
scientifically defensible validation of probability estimates, distributional
assumptions, anomaly evidence, sample-size behavior, or electrical
interpretation.

A strong defense requires one traceable evidence package connecting source
data, analysis code, numerical outputs, figures, manuscript claims, and stated
limitations. Software correctness, statistical adequacy, detector behavior,
and electrical interpretation must be validated separately so that one kind of
evidence is not used to claim another.

## Current baseline and blockers

Accepted baseline evidence includes parser fidelity, complete and unique
observation keys, conversion against the 112677 V ATP base, controlled data
integrity failures, and auditable result-package infrastructure.

Final-result production is blocked by the following known conditions:

1. Existing run configurations and saved packages use mixed P.U. bases. Runs
   based on 100000 V cannot support final comparisons with runs based on
   112677 V.
2. Current K-Means comparison treats highest-centroid membership as anomaly
   evidence even when that cluster represents ordinary high-voltage behavior.
3. Current DBSCAN parameters are not calibrated in a documented feature space
   and can label all target observations as one cluster.
4. Gaussian outputs lack a recorded distribution-adequacy decision and
   uncertainty interval for empirical exceedance.
5. No reviewed ground-truth labels exist for real ATP numerical errors.

No final statistical, anomaly, or comparison claim may be accepted until the
applicable blockers are closed and regenerated artifacts are identified by
new provenance records.

## Validation model

The evidence package SHALL keep four validation layers distinct:

| Layer | Question | Permitted conclusion |
|---|---|---|
| Data validity | Were source values extracted, identified, normalized, and cleaned correctly? | Accepted values represent declared ATP outputs within audited scope |
| Statistical validity | Are descriptive, probability, uncertainty, and distributional calculations appropriate? | Estimates are valid under declared sample and model conditions |
| Detector validity | Does anomaly logic detect defined deviations without misclassifying ordinary structure? | Method detects tested analytical patterns with measured behavior |
| Electrical validity | Is a candidate physically plausible, numerical, defective, or unresolved? | Reviewed case-specific interpretation only |

## Goals

- [ ] Produce one canonical, reproducible analysis matrix using the accepted
  P.U. base and comparable experiment definitions.
- [ ] Validate empirical and model-based probability outputs with explicit
  denominators, uncertainty, assumptions, and reconciliation checks.
- [ ] Replace invalid cluster-label inference with explicit, contextual
  anomaly evidence and diagnostics.
- [ ] Evaluate sample-size convergence, method agreement, controlled anomaly
  detection, and parameter sensitivity.
- [ ] Produce publication-ready tables and figures directly from traceable
  artifacts.
- [ ] Complete methodology, results, discussion, limitations, and conclusion
  in `doc/main.tex` without unsupported causal claims.
- [ ] Deliver a defense evidence index mapping every thesis claim to code,
  data, configuration, output, figure, and manuscript location.

## Out of scope

| Item | Reason |
|---|---|
| Automatic insulation-level recommendation | Explicitly excluded from academic scope |
| Company expert-system logic | Protected scope outside the thesis |
| Automatic physical-versus-numerical causal classification | Requires case-specific electrical and waveform evidence |
| Automatic removal of anomaly candidates | Review must remain traceable and reversible |
| Claiming universal probabilities | Estimates are conditional on configured ATP experiments |
| Claiming real-error accuracy from injected data | Synthetic labels represent interventions, not ATP causation |
| Rebuilding the electrical network model | Feature validates analysis of existing declared cases |
| Creating the oral-defense slide deck | This feature produces manuscript-ready evidence, not slides |
| General support for every ATP output layout | Parser validity remains limited to audited layouts |

## Prerequisite gates

Final evidence generation SHALL NOT begin until these gates pass:

1. Every included run uses the accepted 112677 V P.U. base or is explicitly
   isolated as a non-comparable historical result.
2. Every included source has verified identity, expected run count, complete
   terminal-phase keys, and input hash.
3. K-Means cluster identity is descriptive only; anomaly evidence uses an
   explicit score and threshold.
4. DBSCAN exposes preprocessing, effective parameters, applicability status,
   cluster count, noise count, and noise rate.
5. Thresholds, grouping keys, feature definitions, scaling, random states,
   and calibration policies are frozen before final target-data execution.
6. Final configurations write to new result directories and do not overwrite
   historical packages without preservation and provenance.

---

## User stories

### P1: Build the canonical defense dataset matrix ⭐ MVP

**User story:** As a researcher, I want one validated dataset matrix so that
all final comparisons use compatible sources, units, scopes, and identifiers.

**Why P1:** Comparisons across mixed voltage bases or experiment definitions
would invalidate every downstream table and figure.

**Acceptance criteria:**

1. WHEN a case enters the final matrix THEN the system SHALL record scenario,
   source path, source hash, expected and effective run counts, terminals,
   phases, base voltage, time window, and experiment assumptions.
2. WHEN SRPI and CRPI cases are included THEN the system SHALL preserve their
   scenario identity and SHALL analyze them separately before any declared
   comparison or aggregation.
3. WHEN 50, 100, 200, 1,000, and 10,000 simulation cases are compared THEN
   every case SHALL use 112677 V and the same declared event definition.
4. WHEN datasets are nested, overlapping, or independently generated THEN the
   matrix SHALL record that relationship and qualify independence claims.
5. WHEN a configuration uses 100000 V or lacks required provenance THEN the
   system SHALL exclude it from final comparable results and report the exact
   reason.
6. WHEN final observations are materialized THEN every row SHALL remain
   traceable to source file, simulation, terminal, phase, original voltage,
   normalized voltage, and occurrence time.

**Independent test:** Load the final matrix manifest and verify all ten
SRPI/CRPI size combinations, accepted bases, counts, hashes, and unique row
keys without reading generated prose.

### P1: Produce validated descriptive and probability evidence ⭐ MVP

**User story:** As a researcher, I want empirical probabilities and
descriptive statistics with uncertainty so that overvoltage claims have
auditable numerical support.

**Why P1:** A probability without event definition, count, denominator, and
uncertainty cannot support a scientific conclusion.

**Acceptance criteria:**

1. WHEN a terminal-phase group is analyzed THEN the system SHALL report count,
   valid count, mean, sample standard deviation, median, quartiles, selected
   percentiles, minimum, and maximum.
2. WHEN an exceedance threshold is evaluated THEN the system SHALL report
   comparison operator, threshold, occurrence count, denominator, empirical
   probability, percentage, and a documented binomial confidence interval.
3. WHEN ATP frequency, cumulative-frequency, or exceedance tables are
   available THEN the system SHALL reconcile them with direct observation
   counts within a tolerance justified by printed precision and binning.
4. WHEN a threshold lies outside the observed range THEN the system SHALL
   return the valid empirical boundary result without extrapolation.
5. WHEN counts, boundaries, units, or denominators disagree THEN the system
   SHALL mark the probability result invalid or qualified and SHALL preserve
   both source and recalculated values.
6. WHEN probability artifacts are exported THEN every row SHALL include
   scenario, sample size, terminal, phase, unit, event definition, calculation
   source, exclusions, and validation status.

**Independent test:** Recompute selected groups from raw observations and
match descriptive values, event counts, empirical probabilities, confidence
interval inputs, and ATP reconciliation status.

### P1: Evaluate distributional adequacy ⭐ MVP

**User story:** As a researcher, I want Gaussian adequacy evaluated before
using Gaussian tail inference so that model-based probabilities are not
presented as validated by assumption alone.

**Why P1:** Switching-time input distributions do not establish Gaussian
output-peak distributions.

**Acceptance criteria:**

1. WHEN a Gaussian model is fitted THEN the system SHALL record group scope,
   sample size, fitted parameters, fitting policy, and excluded observations.
2. WHEN adequacy is evaluated THEN the system SHALL generate a histogram with
   fitted density, a Q-Q plot, tail diagnostics, and at least one documented
   quantitative goodness-of-fit result.
3. WHEN a goodness-of-fit method is selected THEN its statistic, reference or
   calibration method, significance level, limitations, and decision SHALL be
   recorded before final results are interpreted.
4. WHEN empirical and Gaussian exceedance are both available THEN the system
   SHALL report both and their absolute and relative differences where
   mathematically defined.
5. WHEN adequacy is rejected, inconclusive, or unavailable THEN empirical
   exceedance SHALL remain primary and Gaussian inference SHALL be visibly
   qualified in tables, plots, and manuscript text.
6. WHEN large samples make formal tests highly sensitive THEN discussion SHALL
   combine test results with graphical and effect-size evidence rather than
   equating a p-value with practical invalidity.

**Independent test:** Analyze fixtures representing approximately normal,
skewed, heavy-tailed, multimodal, zero-variance, and undersized samples; verify
artifacts and inference status for each class.

### P1: Correct and contextualize anomaly evidence ⭐ MVP

**User story:** As a researcher, I want explicit anomaly scores within
comparable groups so that ordinary terminal, phase, or cluster differences are
not mislabeled as anomalies.

**Why P1:** Current highest-centroid inference and inert DBSCAN configuration
cannot support final anomaly claims.

**Acceptance criteria:**

1. WHEN K-Means assigns cluster labels THEN labels SHALL represent descriptive
   membership only and SHALL NOT create an anomaly flag from ordinal identity.
2. WHEN K-Means contributes anomaly evidence THEN the system SHALL use a
   recorded distance or sparsity score, threshold policy, fitted threshold,
   group keys, feature space, scaling policy, and random state.
3. WHEN DBSCAN contributes anomaly evidence THEN the system SHALL record its
   scaled feature space, parameter source, effective parameters,
   applicability, cluster count, noise count, and noise rate per group.
4. WHEN multiple terminals or phases are present THEN anomaly models and
   thresholds SHALL operate within explicit comparable groups unless a
   documented physical rationale supports a joint model.
5. WHEN one or more methods flag an observation THEN exported reasons SHALL
   list only explicit Boolean method criteria that were met.
6. WHEN a method is non-applicable or degenerate THEN it SHALL not count as
   agreement, disagreement, validity, or anomaly evidence.
7. WHEN a dense upper-voltage cluster represents recurring valid behavior THEN
   its full membership SHALL remain non-anomalous unless individual explicit
   scores exceed their thresholds.
8. WHEN target outputs are described THEN the terms SHALL be "candidate" or
   "analytical evidence," never "confirmed ATP numerical error."

**Independent test:** Run a deterministic fixture with two dense valid
clusters, terminal offsets, isolated points, sparse groups, and degenerate
groups; verify contextual scores, explicit flags, and applicability statuses.

### P1: Validate controlled anomaly detection ⭐ MVP

**User story:** As a researcher, I want labeled controlled perturbations so
that detector behavior can be quantified without inventing labels for real
ATP cases.

**Why P1:** Real target data have no reviewed ground truth for numerical
errors.

**Acceptance criteria:**

1. WHEN controlled data are created THEN original source files SHALL remain
   unchanged and interventions SHALL occur only in copied or derived datasets.
2. WHEN an intervention is injected THEN a manifest SHALL record row or run
   identity, original value, injected value, intervention family, intensity,
   contamination rate, random seed, and generator version.
3. WHEN benchmark families are executed THEN they SHALL include point,
   contextual, and collective perturbations, plus clean baseline controls.
4. WHEN contamination rates are evaluated THEN the benchmark SHALL include
   the predeclared 1%, 5%, and 10% conditions or document why a condition is
   infeasible for a group.
5. WHEN development and evaluation sets are formed THEN splitting SHALL occur
   by simulation run and source lineage so related terminals and phases do not
   leak across the split.
6. WHEN methods are evaluated THEN scaling, calibration, and thresholds SHALL
   fit development data only.
7. WHEN benchmark results are reported THEN each intervention family,
   intensity, and method SHALL expose TP, FP, TN, FN, precision, recall, F1,
   and false-positive rate with non-applicable metrics marked explicitly.
8. WHEN results are interpreted THEN success SHALL mean detection of the
   declared intervention, not proof of ATP numerical-error diagnosis.

**Independent test:** Regenerate the same benchmark from its manifest and
seed, reproduce identical labels, and independently recompute every confusion
matrix and metric.

### P1: Evaluate convergence across sample sizes ⭐ MVP

**User story:** As a researcher, I want cross-sample comparisons so that the
defense shows whether reported estimates stabilize as simulation count grows.

**Why P1:** One sample size cannot demonstrate sampling consistency, and
density methods change behavior with sample size.

**Acceptance criteria:**

1. WHEN 50, 100, 200, 1,000, and 10,000 cases are compared THEN the report
   SHALL use compatible scenario, base, terminal, phase, threshold, grouping,
   and method policies.
2. WHEN each size is analyzed THEN the report SHALL include descriptive
   statistics, selected percentiles, empirical exceedance, confidence-interval
   width, fitted model status, candidate counts, and candidate rates.
3. WHEN consecutive sizes are compared THEN the report SHALL expose absolute
   and relative changes where defined without imposing an unsupported expected
   anomaly percentage.
4. WHEN a reference size is used THEN it SHALL be described as a high-sample
   empirical reference, not ground truth.
5. WHEN results stabilize THEN text SHALL describe sampling consistency only;
   it SHALL NOT infer detector accuracy from stability.
6. WHEN datasets are not nested or independent assumptions are uncertain THEN
   comparison methods and manuscript language SHALL state that limitation.

**Independent test:** Recalculate the cross-sample table from final per-run
artifacts and reproduce every displayed value and comparison status.

### P1: Compare scenarios, terminals, phases, and methods ⭐ MVP

**User story:** As a researcher, I want structured comparisons so that
differences are interpreted in their electrical and analytical context.

**Why P1:** Aggregation can hide phase, terminal, and scenario behavior or turn
normal location effects into false anomaly evidence.

**Acceptance criteria:**

1. WHEN SRPI and CRPI are compared THEN the report SHALL state their switching
   definitions and compare only compatible event measures.
2. WHEN terminals are compared THEN each terminal SHALL retain its line
   position and group identity.
3. WHEN phases are compared THEN all three phases SHALL remain traceable to the
   same run and scenario without treating phase asymmetry alone as an error.
4. WHEN statistical and anomaly methods are compared THEN the report SHALL
   distinguish $3\sigma$, robust statistical criteria, K-Means evidence, and
   DBSCAN evidence.
5. WHEN methods agree or disagree THEN a row-level or aggregated artifact
   SHALL preserve each method's explicit status and reason.
6. WHEN multiple comparisons are presented THEN the report SHALL declare
   whether analysis is descriptive, exploratory, or inferential and SHALL
   qualify multiplicity where inferential claims are made.

**Independent test:** Select one source run and trace its three phases and
three terminals through every comparison artifact without identity loss.

### P1: Evaluate parameter sensitivity and stability ⭐ MVP

**User story:** As a researcher, I want predeclared sensitivity experiments so
that conclusions are not artifacts of one convenient parameter choice.

**Why P1:** K-Means initialization, cluster count, score thresholds, DBSCAN
calibration, and statistical cutoffs can materially change candidate sets.

**Acceptance criteria:**

1. WHEN sensitivity analysis is configured THEN varied parameters, ranges,
   fixed controls, seeds, and evaluation measures SHALL be declared before
   final target results are inspected.
2. WHEN K-Means is evaluated THEN repeated documented seeds and justified
   cluster-count alternatives SHALL be included where applicable.
3. WHEN anomaly thresholds or DBSCAN policies are evaluated THEN the report
   SHALL expose candidate counts, rates, applicability, and candidate-set
   overlap for every policy.
4. WHEN stability is summarized THEN the report SHALL include a documented
   identity-based overlap measure and not rely only on similar candidate rates.
5. WHEN small justified parameter changes cause large result changes THEN the
   conclusion SHALL be marked sensitive and SHALL not present one setting as
   uniquely validated.
6. WHEN an acceptance threshold for stability is used THEN its value and
   rationale SHALL be frozen before final results are generated.

**Independent test:** Reproduce the parameter grid from saved configuration
and verify candidate counts, rates, overlap measures, and sensitivity status.

### P1: Conduct traceable technical review ⭐ MVP

**User story:** As a thesis author, I want representative analytical candidates
reviewed against electrical context so that limitations and case-specific
interpretations are defensible before the examining committee.

**Why P1:** Statistical and clustering evidence alone cannot determine physical
or numerical cause.

**Acceptance criteria:**

1. WHEN review cases are selected THEN the sample SHALL cover method
   agreement, method disagreement, high-score candidates, boundary cases, and
   non-flagged controls across available scenarios and groups.
2. WHEN a case is reviewed THEN the record SHALL include source identity,
   simulation, terminal, phase, signed source maximum, P.U. value, occurrence
   time, switching conditions, other phases and terminals, and method evidence.
3. WHEN waveform data or repeat simulation evidence is available THEN the
   review SHALL preserve its source, parameters, integration step, comparison
   tolerance, and observed behavior.
4. WHEN waveform or repeat-simulation evidence is unavailable THEN the case
   SHALL remain analytically classified or unresolved and SHALL not receive a
   causal label.
5. WHEN review concludes THEN its status SHALL be one of data defect,
   suspected numerical artifact, physically plausible extreme, or unresolved,
   with reviewer, date, evidence, and rationale.
6. WHEN no qualified independent electrical reviewer participates THEN the
   manuscript SHALL state that limitation explicitly.

**Independent test:** Trace every review-table conclusion back to immutable
source records and supporting evidence without relying on figure appearance.

### P1: Generate publication-ready graphical evidence ⭐ MVP

**User story:** As a reader, I want consistent, self-contained figures so that
I can understand distributions, comparisons, uncertainty, and anomaly
evidence without reverse-engineering code or legends.

**Why P1:** Figures are core defense evidence, not decoration.

**Acceptance criteria:**

1. WHEN a final figure is generated THEN it SHALL be produced by versioned
   code from a saved machine-readable artifact and configuration.
2. WHEN a figure displays data THEN title, axes, unit, scenario, sample size,
   terminal, phase, method context, and relevant thresholds SHALL be explicit
   in the figure or caption.
3. WHEN clusters and anomalies share a plot THEN color SHALL encode descriptive
   cluster membership and a separate marker SHALL encode anomaly evidence.
4. WHEN empirical and Gaussian exceedance are compared THEN both curves,
   empirical uncertainty where applicable, threshold markers, sample count,
   and adequacy status SHALL be visible or captioned.
5. WHEN convergence is displayed THEN a common scale and clearly distinguished
   sample sizes SHALL be used without implying independence that was not
   established.
6. WHEN method agreement is displayed THEN agreement, disagreement,
   non-applicable status, and candidate counts SHALL remain distinguishable.
7. WHEN sensitivity is displayed THEN varied parameter, fixed controls, and
   stability measure SHALL be identifiable.
8. WHEN figures are exported THEN publication versions SHALL use vector output
   where supported or at least 300 DPI raster output, readable fonts,
   colorblind-safe distinctions, and grayscale-compatible markers.
9. WHEN a figure appears in `main.tex` THEN its caption SHALL state what was
   measured, scope, interpretation, and key limitation; caption SHALL not claim
   causal error classification without supporting review evidence.

**Independent test:** Regenerate all manuscript figures from the final
manifest, compare hashes or declared nondeterministic fields, and inspect a
grayscale rendering at final document size.

### P1: Produce defense tables and machine-readable data ⭐ MVP

**User story:** As an examiner, I want concise tables backed by downloadable
data so that every numerical claim can be audited.

**Why P1:** Screenshots and manually copied values are not reproducible
evidence.

**Acceptance criteria:**

1. WHEN final tables are generated THEN machine-readable source tables SHALL
   be saved separately from LaTeX presentation tables.
2. WHEN a table reports probability THEN it SHALL include event count,
   denominator, estimate, uncertainty, group scope, and validation status.
3. WHEN a table reports anomaly performance THEN it SHALL include confusion
   counts before derived metrics and mark undefined metrics explicitly.
4. WHEN a table reports convergence THEN all sample sizes SHALL share the same
   metric definitions and comparable configuration identifiers.
5. WHEN a table reports technical review THEN analytical evidence and causal
   review conclusions SHALL use separate columns.
6. WHEN values are rounded for the manuscript THEN source precision SHALL be
   preserved in machine-readable data and rounding policy SHALL be documented.
7. WHEN a displayed value is copied into `main.tex` THEN a traceability record
   SHALL identify source artifact, row or group key, generator version, and
   manuscript label.

**Independent test:** Select every numeric table in `main.tex` and reproduce it
from its machine-readable source using one documented command.

### P1: Complete methodology in `main.tex` ⭐ MVP

**User story:** As an examiner, I want methodology to declare every analytical
choice before results so that conclusions can be evaluated against fixed
criteria.

**Why P1:** Current manuscript leaves statistical, probabilistic, and
clustering methodology as future work.

**Acceptance criteria:**

1. WHEN methodology is completed THEN existing TODO placeholders for applied
   statistics, probability, clustering features, parameters, and evaluation
   criteria SHALL be removed or resolved.
2. WHEN data scope is described THEN manuscript SHALL define scenarios,
   sample sizes, observation unit, terminals, phases, P.U. base, event
   definition, inclusion rules, and exclusions.
3. WHEN probability methodology is described THEN manuscript SHALL define
   direct counts, denominator, comparison operators, interval boundaries,
   confidence-interval method, and conditional interpretation.
4. WHEN Gaussian analysis is described THEN manuscript SHALL define fitting,
   adequacy evaluation, decision rule, graphical diagnostics, and fallback to
   empirical evidence.
5. WHEN anomaly methodology is described THEN manuscript SHALL define
   comparable groups, features, scaling, score, threshold, random state,
   applicability, and distinction between cluster membership and anomaly.
6. WHEN controlled experiments are described THEN manuscript SHALL define
   intervention families, rates, intensities, seeds, split policy, metrics,
   and limits of synthetic labels.
7. WHEN convergence and sensitivity are described THEN manuscript SHALL define
   compared configurations, metrics, stability measure, and acceptance or
   qualification rules.
8. WHEN technical review is described THEN manuscript SHALL define case
   selection, evidence fields, conclusion categories, and reviewer limits.
9. WHEN software verification is described THEN manuscript SHALL separate
   code correctness from statistical and electrical validity.

**Independent test:** Trace every methodology choice to configuration,
versioned code, test, or predeclared review protocol before reading results.

### P1: Complete results, discussion, and conclusion in `main.tex` ⭐ MVP

**User story:** As a thesis author, I want results and claims linked to
evidence so that the defense remains accurate under detailed questioning.

**Why P1:** Final defense requires interpreted results, not only validated
infrastructure.

**Acceptance criteria:**

1. WHEN final results are written THEN sections SHALL cover probability and
   distribution adequacy, convergence, method comparison, controlled
   detection, sensitivity, and technical review.
2. WHEN a table or figure is cited THEN prose SHALL state result, scope,
   uncertainty or validation status, and practical interpretation.
3. WHEN methods disagree or hypotheses are not supported THEN discussion SHALL
   report those outcomes rather than omit them.
4. WHEN synthetic performance is discussed THEN prose SHALL not generalize
   measured accuracy to real ATP numerical errors.
5. WHEN stability is discussed THEN prose SHALL not equate stable output with
   accurate detection.
6. WHEN an anomaly candidate lacks electrical evidence THEN prose SHALL not
   label it as physical or numerical.
7. WHEN conclusions are written THEN each objective SHALL be answered with
   evidence, limitation, and completion status.
8. WHEN future work is stated THEN it SHALL distinguish unfinished required
   validation from legitimate post-thesis extensions.

**Independent test:** Build a claim-evidence matrix for every conclusion
paragraph and verify that no claim depends only on software tests, visual
impression, or an unvalidated model assumption.

### P1: Deliver a reproducible defense evidence package ⭐ MVP

**User story:** As a researcher, I want one immutable evidence index so that
the committee or another researcher can reproduce and audit final claims.

**Why P1:** Unlinked files do not establish end-to-end reproducibility.

**Acceptance criteria:**

1. WHEN final analysis runs complete THEN one manifest SHALL list source
   hashes, configurations, code revision, dependency versions, commands,
   outputs, output hashes, generation time, and validation statuses.
2. WHEN deterministic artifacts are regenerated from unchanged inputs and
   code THEN tables and analytical labels SHALL match exactly within declared
   numeric tolerances.
3. WHEN runtime timestamps, image metadata, or other nondeterministic fields
   differ THEN manifest SHALL identify and exclude them from semantic equality
   checks rather than hiding differences.
4. WHEN final evidence is indexed THEN each requirement SHALL map to code,
   tests, data, output artifact, figure or table label, and manuscript section.
5. WHEN a prerequisite or quality gate fails THEN final package status SHALL
   remain incomplete and manuscript SHALL not cite failed outputs as accepted
   evidence.
6. WHEN final verification runs THEN `task format`, `task lint`,
   `task typecheck`, `task test`, and LaTeX compilation SHALL pass on the
   recorded revision.
7. WHEN `main.tex` compiles THEN references, citations, table and figure labels,
   and list entries SHALL resolve without new document errors.

**Independent test:** Reproduce the package in a clean environment from the
recorded revision and inputs, then verify requirement traceability and
semantic artifact equality.

### P2: Compare against robust statistical baselines

**User story:** As a researcher, I want robust baselines so that conclusions do
not depend only on Gaussian $3\sigma$ screening.

**Why P2:** IQR or MAD evidence helps reveal sensitivity to skewness and heavy
tails, but does not replace core empirical probability validation.

**Acceptance criteria:**

1. WHEN robust screening is enabled THEN formula, grouping, threshold policy,
   and applicability SHALL be recorded.
2. WHEN robust and Gaussian criteria are compared THEN agreement and
   disagreement SHALL be reported without assuming either method is ground
   truth.
3. WHEN a group is too small or degenerate THEN robust evidence SHALL return an
   explicit non-applicable status.

**Independent test:** Evaluate symmetric, skewed, heavy-tailed, and
zero-variance fixtures and verify recorded method behavior.

### P2: Add repeat-simulation numerical sensitivity evidence

**User story:** As an electrical reviewer, I want selected runs repeated with
smaller integration steps so that suspected numerical sensitivity has stronger
case-specific evidence.

**Why P2:** Peak-only tables cannot establish waveform or discretization
causation, and reruns may require ATP access outside the software workflow.

**Acceptance criteria:**

1. WHEN a run is repeated THEN physical inputs, realized switching times,
   model version, solver settings, integration steps, and output resolution
   SHALL be preserved.
2. WHEN steps such as $dt$, $dt/2$, and $dt/4$ are compared THEN peak
   magnitude, peak time, and waveform differences SHALL use a predeclared
   engineering tolerance.
3. WHEN sensitivity is observed THEN result SHALL remain evidence for review,
   not automatic proof of numerical error.
4. WHEN repeat simulation is unavailable THEN absence SHALL not block core
   analytical validation but SHALL limit causal conclusions.

**Independent test:** Reproduce one selected case comparison from recorded ATP
inputs and calculate declared differences independently.

---

## Required final graphical set

Final manuscript package SHALL include, where data permit:

1. Validation-chain diagram from ATP source through reviewed conclusion.
2. Dataset-matrix diagram or table for scenario and sample-size coverage.
3. Distribution panel with histogram, fitted density, and Q-Q evidence.
4. Empirical-versus-Gaussian exceedance plot with confidence information.
5. Sample-size convergence plot for primary descriptive and probability
   metrics.
6. Cluster plot separating descriptive color from anomaly markers.
7. Method-agreement matrix or upset-style count visualization.
8. Controlled-benchmark performance plot by intervention and intensity.
9. Parameter-sensitivity or candidate-set stability plot.
10. Representative-candidate context plot or auditable review table.

Every final figure SHALL have a machine-readable source and SHALL be generated
without manual numerical editing.

## Required final data artifacts

The final package SHALL contain machine-readable equivalents of:

- canonical dataset matrix and source manifest;
- cleaned observations and exclusion log;
- descriptive and probability summaries;
- confidence-interval results;
- distribution-adequacy diagnostics;
- cross-sample convergence results;
- explicit per-method anomaly scores, flags, reasons, and applicability;
- controlled-intervention manifest and benchmark metrics;
- sensitivity configurations and stability metrics;
- technical-review records;
- figure-source tables;
- claim-evidence traceability matrix;
- complete provenance and semantic reproduction manifest.

Exact filenames and schema versions belong to design. All schemas SHALL use
explicit types, units, stable group keys, and version identifiers.

## Edge cases

- WHEN a required sample size or scenario is absent THEN comparison SHALL show
  missing coverage and SHALL not interpolate a result.
- WHEN no observations exceed a threshold THEN probability SHALL be zero with
  its count, denominator, and uncertainty interval, not "no result."
- WHEN all observations exceed a threshold THEN probability SHALL be one with
  its count, denominator, and uncertainty interval.
- WHEN confidence-interval assumptions are invalid or inputs are insufficient
  THEN interval SHALL be non-applicable with a reason.
- WHEN a group has fewer rows than a method requires THEN method SHALL be
  non-applicable and SHALL not silently label all rows valid or anomalous.
- WHEN a group has zero variance THEN scaling, Gaussian fitting, and anomaly
  scoring SHALL avoid non-finite outputs and expose degenerate status.
- WHEN every row becomes noise or anomalous THEN output SHALL emit a
  degeneracy warning and require review before interpretation.
- WHEN no candidates are detected THEN reports and plots SHALL remain valid
  and SHALL not treat zero candidates as method failure by definition.
- WHEN methods disagree completely THEN disagreement SHALL remain visible and
  SHALL not be collapsed into one unqualified final label.
- WHEN a metric denominator is zero THEN metric SHALL be undefined or
  non-applicable, never coerced to zero.
- WHEN labels are highly imbalanced THEN confusion counts and precision-recall
  metrics SHALL accompany any aggregate score.
- WHEN candidate rates match across runs but identities differ THEN stability
  SHALL reflect identity mismatch.
- WHEN an old artifact lacks required schema fields THEN reader SHALL reject
  it with a schema-version message rather than infer missing evidence.
- WHEN LaTeX text and generated values disagree THEN package SHALL fail the
  claim-evidence check before acceptance.
- WHEN figure colors become indistinguishable in grayscale THEN markers,
  line styles, or direct labels SHALL preserve meaning.
- WHEN source or generated artifacts contain private company information THEN
  defense package SHALL use approved redaction without breaking provenance.

## Requirement traceability

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| DEF-01 | Build canonical dataset and source matrix | P1 | Pending |
| DEF-02 | Enforce accepted P.U. base and comparable configurations | P1 | Pending |
| DEF-03 | Preserve row-level source and experiment identity | P1 | Pending |
| DEF-04 | Produce descriptive statistics with explicit scope | P1 | Pending |
| DEF-05 | Produce empirical exceedance with counts and uncertainty | P1 | Pending |
| DEF-06 | Reconcile direct and ATP-provided probability evidence | P1 | Pending |
| DEF-07 | Evaluate and qualify Gaussian adequacy | P1 | Pending |
| DEF-08 | Separate cluster membership from anomaly evidence | P1 | Pending |
| DEF-09 | Produce contextual K-Means scores and thresholds | P1 | Pending |
| DEF-10 | Calibrate and diagnose DBSCAN per comparable group | P1 | Pending |
| DEF-11 | Compare explicit per-method anomaly evidence | P1 | Pending |
| DEF-12 | Create reproducible controlled perturbation datasets | P1 | Pending |
| DEF-13 | Measure controlled detection performance | P1 | Pending |
| DEF-14 | Evaluate convergence across five sample sizes | P1 | Pending |
| DEF-15 | Compare SRPI/CRPI, terminals, phases, and methods | P1 | Pending |
| DEF-16 | Evaluate parameter sensitivity and candidate stability | P1 | Pending |
| DEF-17 | Conduct traceable technical case review | P1 | Pending |
| DEF-18 | Generate publication-ready figures | P1 | Pending |
| DEF-19 | Generate traceable manuscript and source tables | P1 | Pending |
| DEF-20 | Complete statistical and anomaly methodology in manuscript | P1 | Pending |
| DEF-21 | Complete results, discussion, limitations, and conclusion | P1 | Pending |
| DEF-22 | Build claim-evidence traceability matrix | P1 | Pending |
| DEF-23 | Produce immutable reproducibility manifest | P1 | Pending |
| DEF-24 | Pass software and LaTeX quality gates | P1 | Pending |
| DEF-25 | Compare robust statistical baselines | P2 | Pending |
| DEF-26 | Add repeat-simulation numerical sensitivity evidence | P2 | Pending |

**Coverage:** 26 requirements; 0 mapped to design; 0 mapped to tasks.

## Success criteria

- [ ] All final comparable configurations use 112677 V and record source
  hashes, experiment scope, and effective sample counts.
- [ ] No production or reporting path treats highest-centroid membership as
  anomaly evidence.
- [ ] Every probability claim includes event count, denominator, uncertainty,
  group scope, and calculation source.
- [ ] Every Gaussian inference exposes adequacy status and empirical
  comparison.
- [ ] Controlled benchmark reproduces labels and confusion matrices from a
  saved manifest.
- [ ] Cross-sample table covers 50, 100, 200, 1,000, and 10,000 simulations
  under comparable policies.
- [ ] Sensitivity evidence reports candidate identity overlap, not only rates.
- [ ] Technical review records unresolved cases without forcing causal labels.
- [ ] Every manuscript table and figure regenerates from machine-readable
  sources and recorded code.
- [ ] Every conclusion maps to evidence, scope, limitation, and requirement.
- [ ] `main.tex` contains no unresolved required-analysis TODO and compiles
  without new errors or unresolved references.
- [ ] `task format`, `task lint`, `task typecheck`, and `task test` pass on the
  recorded final revision.
- [ ] Manuscript makes no automatic insulation recommendation and no
  unsupported claim that an analytical candidate is a numerical ATP error.

## Design decisions requiring approval

Design phase must select and justify:

1. Binomial confidence-interval method and confidence level.
2. Distribution-adequacy test or calibrated diagnostic and its decision rule.
3. Robust baseline policy, including IQR or MAD thresholds.
4. K-Means comparable groups, features, score, and threshold policy.
5. DBSCAN scaling and fixed-versus-calibrated parameter policy.
6. Controlled-intervention magnitudes and minimum evaluable group size.
7. Candidate-set overlap measure and any stability acceptance threshold.
8. Technical-review sampling rule and reviewer requirements.
9. Final artifact directory, schemas, versions, and deterministic-comparison
   policy.
10. Figure style system, source-table contract, and LaTeX integration method.

These decisions must be recorded before final target-data results are used to
select favorable parameters or acceptance thresholds.

