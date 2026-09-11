# Observation structure

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
