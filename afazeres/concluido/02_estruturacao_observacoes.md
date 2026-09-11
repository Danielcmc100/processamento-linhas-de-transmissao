# Observation structure

## Current acceptance — 2026-09-10

**Concluído.** Accepted for the ten selected SRPI/CRPI files after parser repair.
Reviewer: Codex; no independent human review is claimed.
Evaluated revision: `a90451eef2271e39d905862734c2d29f4d95132f`.

### Required evidence before Concluído

- [x] All five CRPI files regenerated after parser correction: 102,150 complete
  observations; SRPI regression retains another 102,150 observations.
- [x] All nine terminal/phase combinations in every simulation, with unique
  source-file/simulation/terminal/phase keys across the ten-file scope.
- [x] Independent phase-A voltage/time references: CRPI 30/30 and SRPI 30/30
  match at first/last runs. Numerical coverage is sampled, not exhaustive.
- [x] Revision, hashes, procedure, results, limitations, reviewer, date,
  decision and thesis location recorded in the current report below.

### Evidence and decision

- [Current report](../../doc/observation_structure_validation_report.md).
- [Manifest](../../doc/evidence/observation_validation_2026-09-10.sha256).
- [CRPI execution](../../doc/evidence/observation_crpi_audit_2026-09-10.txt).
- [SRPI execution](../../doc/evidence/observation_srpi_audit_2026-09-10.txt).
- [Parser prerequisite](01_parser_arquivos_atp.md).
- Thesis: `doc/main.tex`, subsection `Escopo e validação do parser`, paragraph
  beginning “Observation structure was revalidated”.

The 204,300 rows satisfy exhaustive key completeness and uniqueness for the
selected files; all 60 numerical checkpoints agree. Seven preprocessing tests
pass. This supports acceptance of scalar-observation structure, not electrical
P.U. justification, waveforms, Gaussian adequacy or anomaly interpretation.
Old CRPI downstream artifacts require regeneration and separate validation.
Reopen for other layouts or changes invalidating the recorded evidence.

## Historical reopening — superseded by current acceptance


## Reopened validation — 2026-09-10

**Validando.** All five examined CRPI sizes produce duplicate terminal/phase
keys and omit `T_OPO` despite the expected total row count. The historical
acceptance below is restricted to SRPI and does not validate CRPI.

Evidence: [CRPI findings](../../doc/crpi_validation_findings.md).
Prerequisite: [TCCKL-8 parser validation](01_parser_arquivos_atp.md).

### Required evidence before Concluído

- [ ] After the parser correction, verify all five CRPI files contain exactly
  one observation for every simulation, terminal, and phase combination.
- [ ] Require all nine combinations of `T_MAN`, `1_2LT`, `T_OPO` and A/B/C;
  require uniqueness of source file, simulation, terminal, and phase.
- [ ] Compare extracted voltages and times against independent CRPI records,
  not merely row counts; preserve the SRPI regression evidence.
- [ ] Record revision, input hashes, procedure, results, limitations, reviewer,
  acceptance date, decision, and thesis location before closing again.

## Historical record (superseded current status)

## Status

**Completed.** Accepted on 2026-09-09 for the selected scalar-maximum
structure scope.

## Acceptance evidence

- Validation report:
  [`doc/observation_structure_validation_report.md`](../../doc/observation_structure_validation_report.md).
- Independent ATP records and source hashes:
  [`doc/evidence/parser_audit_checkpoints.csv`](../../doc/evidence/parser_audit_checkpoints.csv).
- Reproducible audit: `scripts/audit_observation_structure.py`.
- Implementation: `src/services/preprocessing.py`.
- Regression coverage: `tests/test_preprocessing.py`.
- Thesis location: `doc/main.tex`, subsection
  `Escopo e validação do parser`.
- Reviewed revision: `d2b1feb5d039353222d03c7aee3ef10ca8e8b3c2`.
- Reviewer: Codex, comparing the output with independently transcribed ATP
  source records.

## Scope and decision

One observation is one scalar phase-to-ground voltage maximum identified by
source file, simulation, terminal, and phase. Completeness and uniqueness were
confirmed for 102,150 rows from five selected files spanning 50 to 10,000
simulations. All 30 independently transcribed terminal records matched their
source-file, simulation, terminal, phase, voltage-transformation, and time
mappings. A regression test also confirmed that source paths distinguish equal
simulation identifiers from multiple files.

The structure is accepted because its observation semantics, multi-file
treatment, completeness rule, uniqueness rule, source mapping, reproduction
procedure, and thesis description are explicit and verified.

## Limitations

- The accepted layout covers `T_MAN/SRPI/CASO-COMPLETO/SDEF`; other scenarios
  require their expected terminal-phase layout to be checked.
- The P.U. transformation is structurally verified with an explicit base, but
  the electrical justification of that base belongs to TCCKL-10.
- The table contains scalar maxima, not waveforms, and does not support claims
  about duration, frequency, rate of change, or oscillatory content.
- Physical-versus-numerical interpretation remains outside this card.

Reopen validation if the observation key, ATP layout, selected terminals, or
stored waveform scope changes.
