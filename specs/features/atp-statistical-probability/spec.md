# ATP Statistical Case Probability Specification

**Status:** Draft
**Source:** `calculo_probabilidade_caso_estatistico_ATP.md`
**Primary source:** Orlando P. Hevia, "Gráficos Estadísticos con el
GTPPLOT," CAUE - Comité Argentino de Usuarios del EMTP, 2000,
`2000-N4-Estati.pdf` (10 pages)
**Related feature:**
`specs/features/atp-data-processing-validation/spec.md`

## Problem statement

ATP statistical studies generate one peak value per configured variable and
energization. Researchers need a reproducible way to estimate interval and
exceedance probabilities from those results without confusing the input
distribution of switching times with the empirical distribution of electrical
outputs.

The analysis must preserve the experiment conditions that define the sampled
probability space, make interval boundaries explicit, and avoid presenting a
simulation-conditioned empirical frequency as a universal physical
probability.

## Goals

- [ ] Represent each ATP statistical experiment with its sample count,
  switching assumptions, monitored variable, units, and source provenance.
- [ ] Calculate empirical probabilities for result intervals and exceedance
  thresholds from peak observations or ATP statistical tables.
- [ ] Validate frequency, cumulative-frequency, and exceedance data before
  using them in analysis.
- [ ] Calculate auditable descriptive statistics from ungrouped observations.
- [ ] Support the GTPPLOT 2% overvoltage approximation while stating its
  assumptions and distinguishing it from direct empirical exceedance.
- [ ] Produce reproducible tables and exceedance curves suitable for TCC
  evidence.

## Out of scope

| Item | Reason |
|---|---|
| Running or controlling ATP simulations | This feature analyzes completed statistical results |
| Selecting switching-time distributions | Experimental design remains an engineering input |
| Claiming that output peaks follow the input distribution | ATP transformation can produce a different output distribution |
| Proving that an extreme value is physical or numerical | Requires anomaly and electrical-domain evidence |
| Automatic insulation-level recommendations | Explicitly excluded from TCC scope |
| Generalizing results beyond configured conditions | Estimates are conditional on the simulated model |

---

## User stories

### P1: Capture statistical experiment context ⭐ MVP

**User story:** As a researcher, I want each probability result tied to the
ATP experiment that generated it so that the estimate remains reproducible
and scientifically qualified.

**Why P1:** A probability has no valid interpretation without its sampling
conditions and denominator.

**Acceptance criteria:**

1. WHEN an ATP statistical result is analyzed THEN the system SHALL record
   `NENERG` or `KNT` as the expected number of energizations.
2. WHEN experiment metadata is available THEN the system SHALL record the
   switching-time distribution, its parameters, breaker grouping or
   dependence, network scenario, monitored variable, unit, and phase or
   terminal scope.
3. WHEN both `NENERG` and `KNT` are available THEN the system SHALL verify that
   they agree and SHALL reject or explicitly flag a mismatch.
4. WHEN a result is reported THEN the system SHALL state that its probability
   estimate is conditional on the configured statistical model.
5. WHEN multiple variables are represented by one ATP group THEN the system
   SHALL identify the observation as the maximum peak within that group.
6. WHEN ATP calls an output a peak THEN the system SHALL preserve the source
   convention that tabulated peak magnitudes are treated as positive values.

**Independent test:** Analyze fixture metadata containing 1,000 energizations
and verify that output records the denominator, distribution assumptions,
variable identity, units, and conditional interpretation.

### P1: Validate ATP statistical table semantics ⭐ MVP

**User story:** As a researcher, I want ATP table columns interpreted and
validated consistently so that probability calculations do not silently use
corrupt counts or ambiguous bins.

**Why P1:** Frequency and cumulative-frequency errors directly invalidate
probability estimates.

**Acceptance criteria:**

1. WHEN a statistical table is loaded THEN the system SHALL identify bin
   limits, frequency, cumulative frequency, and `Per cent .GE. current value`
   when present.
2. WHEN frequencies are present THEN their sum SHALL equal the effective
   sample count, or the system SHALL emit a validation failure that includes
   both values.
3. WHEN cumulative frequencies are present THEN they SHALL be monotonic,
   bounded from zero through the effective sample count, and consistent with
   the frequency column.
4. WHEN exceedance percentages are present THEN they SHALL be bounded from 0%
   through 100% and non-increasing as the threshold increases.
5. WHEN the ATP table defines a bin as
   \(x_{i-1} < X \le x_i\) THEN the system SHALL preserve that boundary
   convention in calculations and output metadata.
6. WHEN table boundaries cannot be determined from the source THEN the system
   SHALL mark interval calculations as ambiguous instead of assuming boundary
   inclusion.
7. WHEN individual and grouped tables are parsed THEN the system SHALL
   preserve their natural sequence numbers and SHALL identify a grouped table
   from its repeated `SUMMARY` markers.
8. WHEN a grouped table follows individual tables THEN the system SHALL retain
   links to every variable request that formed the group.

**Independent test:** Load one valid table plus fixtures with an incorrect
frequency sum, decreasing cumulative count, increasing exceedance percentage,
and unspecified bin boundaries; verify each expected result.

### P1: Calculate empirical interval probability ⭐ MVP

**User story:** As a researcher, I want the observed probability of a peak
falling within a defined interval so that bounded overvoltage scenarios can be
quantified.

**Why P1:** Interval probability is a core output of the statistical study.

**Acceptance criteria:**

1. WHEN an interval and ungrouped peak observations are provided THEN the
   system SHALL count observations using the requested boundary convention and
   calculate \(P(X \in I) = N(I) / N\).
2. WHEN an interval exactly matches one ATP bin THEN the system SHALL calculate
   its probability from that bin's frequency divided by the effective sample
   count.
3. WHEN an interval aligns with two available exceedance thresholds THEN the
   system SHALL support calculating its probability by subtracting the upper
   exceedance probability from the lower exceedance probability.
4. WHEN direct-count and exceedance-difference methods are both applicable
   THEN the system SHALL compare them within documented rounding tolerance and
   flag disagreement.
5. WHEN an interval cuts through a table bin and ungrouped observations are
   unavailable THEN the system SHALL report that exact probability cannot be
   recovered from grouped data.
6. WHEN probability is returned THEN the output SHALL include occurrence
   count, denominator, decimal probability, percentage, interval, and boundary
   convention.

**Independent test:** Using 1,000 observations with 92 values in
\(2.0 \le X < 2.2\), verify a result of 0.092 and 9.2% with count and boundary
metadata.

### P1: Calculate empirical exceedance probability ⭐ MVP

**User story:** As a researcher, I want the observed probability of a peak
meeting or exceeding a threshold so that overvoltage limits can be evaluated.

**Why P1:** Exceedance is the primary probability question for insulation and
transient studies.

**Acceptance criteria:**

1. WHEN ungrouped peak observations and threshold \(x\) are provided THEN the
   system SHALL calculate
   \(P(X \ge x) = N(X \ge x) / N\).
2. WHEN an ATP row contains `Per cent .GE. current value` for the requested
   threshold THEN the system SHALL preserve it as the ATP-provided empirical
   exceedance estimate.
3. WHEN only cumulative frequency is available THEN the system SHALL calculate
   exceedance using documented bin semantics and SHALL label the result as
   derived from grouped data.
4. WHEN ATP-provided and direct-count estimates are both available THEN the
   system SHALL report both, their absolute difference, and whether the
   difference is explained by table rounding or binning.
5. WHEN a threshold is outside the observed range THEN the system SHALL return
   the mathematically valid empirical boundary result without extrapolating
   beyond the sample.
6. WHEN probability is returned THEN the output SHALL include exceedance
   count, denominator, decimal probability, percentage, threshold, comparison
   operator, and calculation source.

**Independent test:** Using 1,000 observations with 137 values greater than or
equal to 2.0 P.U., verify a result of 0.137 and 13.7% and reconcile it with the
ATP-provided percentage.

### P1: Calculate descriptive statistics ⭐ MVP

**User story:** As a researcher, I want descriptive statistics calculated from
peak observations so that the statistical sample can be characterized and
audited against ATP output.

**Why P1:** Mean and dispersion support data validation and later probabilistic
interpretation.

**Acceptance criteria:**

1. WHEN ungrouped peak observations are available THEN the system SHALL
   calculate arithmetic mean, sample variance using denominator \(N-1\), and
   sample standard deviation.
2. WHEN ATP-provided ungrouped statistics are available THEN the system SHALL
   compare calculated and reported values using documented numerical
   tolerance.
3. WHEN grouped and ungrouped statistics are both present THEN the system
   SHALL preserve them as distinct results and SHALL prefer ungrouped values
   for exact sample summaries.
4. WHEN fewer than two valid observations exist THEN sample variance and
   standard deviation SHALL be non-applicable with a clear reason.
5. WHEN non-finite observations are encountered THEN the system SHALL reject
   them or report an explicit exclusion count according to the configured data
   quality policy.

**Independent test:** Reproduce the reference ungrouped mean, sample variance,
and standard deviation within configured tolerance.

### P2: Calculate the GTPPLOT 2% overvoltage approximation

**User story:** As a researcher, I want to reproduce the GTPPLOT 2%
overvoltage value so that ATP reports can be checked and discussed accurately.

**Why P2:** Useful compatibility result, but it depends on a distributional
approximation and does not replace direct empirical exceedance.

**Acceptance criteria:**

1. WHEN ungrouped mean and standard deviation are valid THEN the system SHALL
   calculate \(X_{2\%} = \bar{X} + 2.0537494s\).
2. WHEN the approximation is reported THEN the system SHALL label it as a
   model-based 2% exceedance level and SHALL NOT label it as an empirical
   observation count.
3. WHEN a direct empirical exceedance curve is available THEN the system SHALL
   report empirical exceedance at \(X_{2\%}\) beside the approximation.
4. WHEN distributional assumptions have not been validated THEN the output
   SHALL mark the approximation as not validated for inferential use and SHALL
   NOT present the nominal 2% level as an observed empirical probability.
5. WHEN the approximation is used for inference THEN the system SHALL expose
   the relevant distribution-adequacy result and its validation status.
6. WHEN grouped and ungrouped summaries are present THEN the system SHALL
   calculate the 2% level independently from each summary's own mean and
   standard deviation and SHALL NOT transfer a value between columns.
7. WHEN a printed GTPPLOT 2% value disagrees with the value recomputed from
   its displayed column inputs THEN the system SHALL preserve both values and
   emit a source-consistency warning.

**Independent test:** Using mean 1.78070337 P.U., standard deviation
0.319469262 P.U., and coefficient 2.0537494, verify 2.43681318 P.U. within
rounding tolerance. Using grouped mean 1.78145000 P.U. and standard deviation
0.319801768 P.U., verify 2.43824269 P.U. and flag that the primary source's
printed 2% row places these two results under the opposite column headings.

### P2: Configure and present grouped distributions

**User story:** As a researcher, I want reproducible histogram and exceedance
outputs so that ATP statistical results can be inspected and included in the
TCC evidence package.

**Why P2:** Presentation supports interpretation after core probabilities are
validated.

**Acceptance criteria:**

1. WHEN grouped output is configured THEN the system SHALL record `MODTAB`,
   `AINCR`, `XMAXMX`, and `NSTATI` when available.
2. WHEN `MODTAB` equals 1 THEN only individual tables SHALL be requested; WHEN
   it equals 2 THEN only a grouped `SUMMARY` table SHALL be requested; WHEN it
   equals 3 THEN both forms SHALL be requested.
3. WHEN `MODTAB` equals 2 for only one variable THEN the system SHALL flag the
   invalid or ineffective request because ATP does not produce a grouped table
   identical to a single-variable table.
4. WHEN positive `AINCR` is used THEN the system SHALL record it as the bin
   width in the relevant unit.
5. WHEN `AINCR` equals `-NCOMP` THEN the system SHALL record exactly `NCOMP`
   requested compartments and SHALL allow ATP's additional displayed leading
   empty row when the first compartment is not populated.
6. WHEN `NSTATI` equals 1 THEN plotted values SHALL use P.U.; WHEN it equals 2
   THEN plotted values SHALL use physical units; WHEN it equals 0 THEN no
   exceedance curve SHALL be inferred from that setting alone.
7. WHEN any valid `NSTATI` mode is selected THEN GTPPLOT histogram generation
   SHALL remain available independently of exceedance-curve generation.
8. WHEN 10 is added to nonzero `NSTATI` THEN the system SHALL interpret the
   result as the step-curve variant while preserving P.U. or physical-unit
   selection from the base value.
9. WHEN an empirical exceedance curve is generated from grouped data THEN the
   system SHALL support line-segment and step representations and SHALL
   disclose bin boundaries.
10. WHEN tables or plots are exported THEN they SHALL include sample count,
   variable, unit, threshold or bins, experiment identifier, and source
   provenance.

**Independent test:** Generate a histogram and step exceedance curve from a
fixture configured with `AINCR = 0.05` P.U. and `NSTATI = 11`; verify labels,
metadata, P.U. values, and monotonic stepwise exceedance values.

### P2: Validate ATP tabulation requests

**User story:** As a researcher, I want ATP statistical request definitions
captured and validated so that table provenance and grouped-variable semantics
can be reconstructed.

**Why P2:** GTPPLOT reads tables generated by ATP; it does not reconstruct
missing statistical tables from simulation output.

**Acceptance criteria:**

1. WHEN a tabulation request is loaded THEN the system SHALL preserve
   `IBROPT`, `BASE`, variable identifiers, continuation markers, and group
   membership.
2. WHEN `IBROPT` is interpreted THEN values 0, -1, -2, -3, and -4 SHALL map to
   node voltage, branch voltage, branch current, branch or switch power, and
   branch or switch energy, respectively.
3. WHEN `AINCR` is positive and `BASE` is blank or zero THEN the system SHALL
   record ATP's applicable default-base rule for the selected `IBROPT`.
4. WHEN `AINCR` is negative THEN the system SHALL record that ATP ignores the
   supplied `BASE` and derives its own scaling base.
5. WHEN branch variables are requested THEN node names SHALL be interpreted as
   ordered pairs; WHEN node voltages are requested THEN each nonblank node
   name SHALL identify one variable.
6. WHEN a request record exceeds 10 node voltages or 5 branch variables THEN
   the system SHALL reject it or require a valid continuation record.
7. WHEN `CONT.` joins request records THEN the system SHALL treat their
   variables as one group and SHALL require a common compatible base.
8. WHEN a group exceeds 200 variables THEN the system SHALL report that it
   violates the source-defined ATP limit.
9. WHEN no ATP statistical tabulation was requested THEN the system SHALL
   report that GTPPLOT cannot generate its statistical graphs from that `.lis`
   file.
10. WHEN `XMAXMX` is blank or zero THEN the system SHALL treat it as unchanged,
    not as a zero-valued clipping threshold.

**Independent test:** Parse request fixtures covering every `IBROPT`, default
and ignored `BASE`, node and branch identifiers, a `CONT.` group, and invalid
record and group sizes; verify normalized provenance and validation results.

---

## Edge cases

- WHEN the effective sample count is zero THEN the system SHALL reject
  probability calculation and SHALL NOT divide by zero.
- WHEN the observed count differs from `NENERG` or `KNT` THEN the system SHALL
  expose missing or excluded cases and SHALL NOT silently change the
  denominator.
- WHEN duplicate peak values equal a threshold THEN all equal values SHALL be
  included for the \(X \ge x\) operator.
- WHEN a requested interval has equal bounds or reversed bounds THEN the
  system SHALL reject it with a clear validation message.
- WHEN percentages are rounded in ATP output THEN consistency checks SHALL use
  tolerance derived from displayed precision.
- WHEN decimal commas occur in source text THEN parsing SHALL normalize them
  without changing values or units.
- WHEN a table contains mixed P.U. and physical-unit columns THEN the system
  SHALL require explicit column selection and SHALL NOT combine units.
- WHEN one run contains multiple phases, terminals, or monitored variables
  THEN probabilities SHALL be grouped by explicit analysis scope unless an
  ATP-defined maximum group is selected.
- WHEN only grouped data are available THEN output SHALL distinguish exact
  bin counts from approximations inside bins.
- WHEN grouped and ungrouped GTPPLOT summaries contain apparently exchanged
  derived values THEN output SHALL preserve source columns, recompute both
  values, and flag the inconsistency without silently correcting source data.

## Data and artifact requirements

Each probability result SHALL preserve or reference:

- experiment and source-file identity;
- expected and effective sample counts;
- switching distribution and parameters when available;
- breaker dependence or grouping when available;
- network scenario and energization conditions when available;
- monitored variable, phase, terminal, unit, and grouping rule;
- event definition, operator, thresholds, and interval boundaries;
- occurrence count, denominator, decimal probability, and percentage;
- calculation source: ungrouped count, ATP exceedance column, cumulative
  frequency, or approximation;
- bin configuration and rounding tolerance when grouped data are used;
- validation warnings, exclusions, and software version.

## Requirement traceability

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| PROB-01 | Capture sample count and experiment conditions | P1 | Pending |
| PROB-02 | Preserve monitored-variable and grouped-peak identity | P1 | Pending |
| PROB-03 | Validate ATP frequency and cumulative-frequency columns | P1 | Pending |
| PROB-04 | Validate ATP exceedance percentages and bin semantics | P1 | Pending |
| PROB-05 | Calculate interval probability from direct counts | P1 | Pending |
| PROB-06 | Calculate interval probability from aligned exceedance thresholds | P1 | Pending |
| PROB-07 | Calculate empirical exceedance probability | P1 | Pending |
| PROB-08 | Reconcile direct, grouped, and ATP-provided estimates | P1 | Pending |
| PROB-09 | Calculate ungrouped mean and sample dispersion | P1 | Pending |
| PROB-10 | Handle invalid counts, observations, and boundaries explicitly | P1 | Pending |
| PROB-11 | Calculate and qualify the GTPPLOT 2% approximation | P2 | Pending |
| PROB-12 | Record ATP grouping and plotting parameters | P2 | Pending |
| PROB-13 | Generate auditable histogram and exceedance outputs | P2 | Pending |
| PROB-14 | Preserve provenance, units, assumptions, and limitations | P1 | Pending |
| PROB-15 | Preserve and validate ATP tabulation request semantics | P2 | Pending |
| PROB-16 | Recompute grouped and ungrouped 2% levels independently | P2 | Pending |
| PROB-17 | Detect source-column inconsistencies without rewriting source data | P2 | Pending |

**Coverage:** 17 requirements; 0 mapped to design; 0 mapped to tasks.

## Success criteria

- [ ] Reference interval and exceedance examples reproduce 9.2% and 13.7%,
  respectively.
- [ ] Reference 2% calculations produce 2.43824269 P.U. from grouped inputs
  and 2.43681318 P.U. from ungrouped inputs, then flag their reversed placement
  in the primary source's printed 2% row.
- [ ] Direct-count, ATP-table, and cumulative-frequency methods are
  distinguishable and auditable.
- [ ] Invalid totals, non-monotonic cumulative data, and ambiguous bin
  boundaries produce explicit validation results.
- [ ] Every probability artifact states denominator, event definition, unit,
  calculation source, and experiment conditions.
- [ ] Reports describe results as conditional on the configured ATP model and
  make no universal-probability, causal-anomaly, or insulation-decision claim.
- [ ] Automated tests cover valid examples and every listed edge-case class.

## Design decisions requiring approval

The design phase must select the source schema for ATP statistical tables,
the tolerance policy for reconciling printed percentages with direct counts,
the distribution-adequacy gate for inferential use of the 2% approximation,
the parser representation for fixed-column tabulation requests and `CONT.`
groups, and the behavior when expected and effective sample counts differ.
Those choices must preserve raw source values and may not hide missing
simulations, exclusions, or inconsistencies in the primary source.
