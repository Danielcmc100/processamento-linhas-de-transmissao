# CRPI header alignment and observation validation findings

Assessment date: 2026-09-10. Reviewer: Codex.

## Decision and scope

TCCKL-8 and TCCKL-9 return to **Validando** following a CRPI layout defect
found while investigating TCCKL-20. No new scientific acceptance is granted.
The historical independent checkpoints covered SRPI, not CRPI. Their results
remain historical evidence; the broader collection scan checked counts and
parseability, which did not establish correct column alignment for every layout.
Parser repair belongs to TCCKL-8; observation acceptance belongs to TCCKL-9.
TCCKL-20 records the dependency, and TCCKL-21 must defer CRPI analysis until
both checks pass. No application code or thesis text was changed by this record.

## Inputs and provenance

All paths below expand to
`input_files/casos/{size}-simulacoes/casos/T_MAN/{scenario}/CASO-COMPLETO/SDEF/case.lis`.
Only these ten primary files were examined for the findings below.

Reviewed code revision: `7de14cda9aa93dd081802df0130543f756c3c52b`.

| Scenario | Size | SHA-256 |
| --- | ---: | --- |
| SRPI | 50 | `b09fa9d252bab8e2280af63978941e42c8d6c74bc9f8a1cb18d6eac580c6c3a3` |
| SRPI | 100 | `0dce7413ff06953b756c37a8dfa729d2eb06cbbc7d647d48fc8cdff6cf28ce52` |
| SRPI | 200 | `ed2f2e202ed3bab5a149b4ade988e368fadf38e047d02463340d5a298b88a7a8` |
| SRPI | 1000 | `d4e0a28fb48fff28ec6c18c43d17e5d9242ab7c6207264866e3625632431d8df` |
| SRPI | 10000 | `c33f7168904d50407d94258b1b7c297306ae6022747a194cd68d20866eed3199` |
| CRPI | 50 | `e7e7afe2d681037bebb84a2be750498f02d37a4a22215b6cf56a3f83c540a3b6` |
| CRPI | 100 | `37257bbcb82f05491d4e3a8eb4ce50b695c04e8fc9a3824d068bb4a19cfc9a44` |
| CRPI | 200 | `e5ec79c2dcb85c221838347dbaabecdffba2dd0a2ccfbcb894c843bdbfbac459` |
| CRPI | 1000 | `3ae12ea7e2bdc1205eaac6d8f63c2601f1f271a5cb5d6dd1375683e4014a789d` |
| CRPI | 10000 | `90f16ae044cb6c1dee3efbbfcc119b2ae029e8b4f1fa9756ba27dbffd9a189c0` |

## Procedure and findings

The investigation used in-memory Python commands, without saving or changing
simulation outputs. Read each file with `Path.read_text(encoding="iso-8859-1")`
so the loader normalizes line endings, then call `parse_statistical_data`.
Inspect the source header between `otherwise blank space` and the first
`Random switching times for simulation number` marker against parsed headers.

In `src/parser/__init__.py`, `_parse_variable_headers` splits the node line
on whitespace and assigns tokens by index. Leading and internal empty columns
are lost. In the CRPI source, a header group begins with `1_2LTB`, `T_OPOA`,
`T_OPOB`, and `T_OPOC`, whose node cells are blank; the next node token belongs
to the fifth column. The parser incorrectly assigns it to the first column.

Extract observations using `extract_maxima_dataframe`, terminals `T_MAN`,
`1_2LT`, `T_OPO`, and base 100000 V solely to reproduce the existing structural
check. Group by source file, simulation, terminal, and phase. Require exactly
one row for each of the nine terminal/phase combinations in each simulation.

| Scenario | Sizes | Row counts, in size order | Structural result |
| --- | --- | --- | --- |
| SRPI | 50, 100, 200, 1000, 10000 | 450, 900, 1800, 9000, 90000 | Complete and unique |
| CRPI | 50, 100, 200, 1000, 10000 | 450, 900, 1800, 9000, 90000 | Fails completeness and uniqueness |

CRPI extraction loses `T_OPO` and duplicates terminal/phase observations.
For simulation 1 of the 50-run CRPI file, `T_MAN/C`, `1_2LT/C`, and `1_2LT/A`
each appear twice, while all three `T_OPO` phases are absent. Correct total
row counts therefore conceal incorrect observation identity. This is a parsing
and extraction defect, not evidence that the ATP simulation itself failed.

For switching overlap, construct each run's ordered tuple of
`(switch_name, time)` from `switching_times`, then intersect sets for every
pair of sample sizes within each scenario. All ten size-pair intersections
per scenario were empty. Each file contained as many distinct vectors as runs.
SRPI has three switch events per run; CRPI has six, so complete vectors across
scenarios are not a comparable pairing criterion without electrical mapping.

## Required follow-up evidence

- TCCKL-8: regression fixture retaining internal blank header cells; independent
  CRPI source-to-header, signed-maximum, and time checks; retained SRPI regression
  results; documented supported layout and justified acceptance decision.
- TCCKL-9: after parser repair, audit all five CRPI files for the nine expected
  combinations per simulation, unique composite keys, and independent source
  mappings. Update evidence and the thesis where the validated scope changes.
- TCCKL-21: do not consolidate CRPI comparison results before those validations.
- TCCKL-20: define the experimental protocol and cite these dependencies;
  do not absorb the parser repair or observation validation into its scope.

## Limitations

Absence of identical switching vectors at the printed precision does not prove
statistical independence, establish initial random seeds, or demonstrate that
new simulation batches are necessary. The observed `SEEDSV` dump values are
not treated as verified initial seeds. The existing runs remain usable inputs
for investigation once extraction fidelity is established.

The 100000 V base is not electrically validated by this audit. No physical
versus numerical anomaly classification, final method evaluation, software
repair, fresh full test run, or new thesis acceptance was performed.

Historical evidence: [parser report](parser_validation_report.md) and
[observation report](observation_structure_validation_report.md).
