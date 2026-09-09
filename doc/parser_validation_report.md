# ATP Statistical Parser Validation Report

**Validation date:** 2026-09-08  
**Reviewer:** Codex, using an independent source transcription and automated
reproduction  
**Parser revision:** `7b68bd14c15da3f73bc5d6055d9265a75cdf3379`  
**Decision:** Accepted for the supported extraction scope stated below

## Scope and source data

The audit evaluated the main statistical `case.lis` files under
`input_files/casos/`. These files are local thesis inputs and are intentionally
excluded from Git. The five independently checked files use the scenario
`T_MAN/SRPI/CASO-COMPLETO/SDEF` at 50, 100, 200, 1,000, and 10,000 declared
simulations. Their exact paths and SHA-256 digests are recorded in
[`parser_audit_checkpoints.csv`](evidence/parser_audit_checkpoints.csv).

The five files were selected before parsing because they hold the topology,
switching policy, complete equivalent-network case, and no-pre-insertion-
resistor scenario used by the saved sample-size analyses. This validates
parser fidelity for that study path; it does not validate the electrical
interpretation of those simulations.

## Independent reference and procedure

The expected values in the checkpoint CSV were transcribed directly from the
ATP text, without calling production parser functions. For each selected file,
the first and last simulation blocks were inspected at the recorded source
line. Each checkpoint records the run identifier, switch 10 time, and the
signed phase-A maximum and maximum time at `T_MAN`, `1_2LT`, and `T_OPO`.
The variable positions were established from the source header block at lines
1,768--1,783 of each file.

The reproducible comparison was then run from the repository root:

```bash
uv run python -m scripts.audit_parser
```

The audit checks each file digest before comparing values. It also reconciles
the declared `NENERG`, parsed run count, contiguous run identifiers, header
count, and maximum/time pair count. Finally, it parses every main statistical
`case.lis` file to test all layouts currently present in the thesis input
collection.

## Results

All five file hashes matched the recorded sources. All 10 independently
transcribed simulation blocks matched exactly: 10 switch times and 30 signed
maximum/time pairs. No sign or time disagreement was observed.

The complete scan accepted all 235 primary statistical files and 533,450
simulation runs. Every run had one maximum/time pair per parsed header. The
observed layout matrix was identical at every sample size:

| `NENERG` | 42 headers | 43 headers | 48 headers | 49 headers | Files |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 5 | 18 | 6 | 18 | 47 |
| 100 | 5 | 18 | 6 | 18 | 47 |
| 200 | 5 | 18 | 6 | 18 | 47 |
| 1,000 | 5 | 18 | 6 | 18 | 47 |
| 10,000 | 5 | 18 | 6 | 18 | 47 |

Software regression checks additionally demonstrated that a statistical file
is rejected when its declared run count, header block, or maximum/time table
is incomplete. The full project gate passed with 98 tests on the validation
date.

## Supported behavior and limitations

The accepted scope is ATP statistical-overvoltage output using the markers
present in the audited collection: `NENERG`, `otherwise blank space`,
`Random switching times for simulation number`, optional first-run table-dump
text, and `Times of maxima`. Files are decoded as ISO-8859-1 by the loaders.

- A statistical block with missing headers, missing/non-contiguous runs, or
  inconsistent maximum/time counts raises `LisParseError`; partial data is not
  silently returned.
- A `.lis` file without an `NENERG` declaration is treated as unsupported,
  non-statistical output and returns an empty parse result. This allows the
  directory loader to ignore deterministic `shot*.lis` files.
- The audit covers the 235 primary files currently available. A new ATP
  version or layout requires a new regression fixture and renewed audit.
- The parser preserves signed maxima. Downstream P.U. preprocessing applies an
  absolute value; that transformation is outside this card's acceptance.
- This validation establishes source-to-model fidelity. It does not determine
  whether an extreme is a physical event or a numerical ATP artifact.

## Acceptance decision

TCCKL-8 is accepted as scientifically complete for syntactic extraction of
the audited ATP statistical layouts. Acceptance is justified by independent
source checkpoints, exhaustive reconciliation of the available primary files,
explicit failure behavior, reproducible inputs, and regression tests. The
method and its limits are recorded in `doc/main.tex`, subsection
`Escopo e validação do parser`. Electrical interpretation remains assigned to
the later anomaly-validation work and does not block this parser decision.
