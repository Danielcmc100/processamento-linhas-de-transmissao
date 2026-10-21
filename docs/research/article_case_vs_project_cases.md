# Article ATP Case Versus Project Cases

## Scope and source integrity

The article source case is
`coisas/inputs/artigo/original/2000-N4-Statis.lis`, with 1,000 ATP
energizations. It is compared here with the SRPI project case at 1,000
energizations under
`input_files/casos/1000-simulacoes/casos/T_MAN/SRPI/CASO-COMPLETO/SDEF`.

The article's standardized input changes only phase-name placement, for
example `FASEA2` to `FASE2A`, so the project parser can identify phase as the
last character. The `padronizado-100` input additionally changes `NENERG` from
1,000 to 100. These reruns use new random draws and therefore cannot reproduce
the original article table row for row.

## Electrical and numerical model differences

| Property | Article case | Project SRPI case |
|---|---|---|
| Purpose | Small didactic GTPPLOT example | Detailed transmission study |
| Line | One 100 km JMarti line | Segmented 80 km line with midpoint |
| ATP network size | 10 nodes, 3 branches | 100 nodes, 144 branches |
| Sources | 3 | 9 |
| Nonlinear elements | 0 | 18 |
| Receiving network | No receiving equivalent in source case | Equivalent network and terminal equipment |
| Surge arresters | None | Arresters at `T_MAN` and `T_OPO` |
| Source frequency | 50 Hz | 60 Hz |
| Time step | 20 microseconds | 10 microseconds |
| Simulation end | 50 ms | 300 ms |
| Phase-ground base | 100,000 V | 112,677 V |
| Phase-phase base | 100,000 V | 195,161 V |
| Switching mean | 20 ms | 20 ms |
| Independent-switch sigma | 1.000 ms | 0.833 ms |
| Common reference delay | Uniform 0-360 degrees at `STATFR = 60 Hz` | Uniform 0-360 degrees at 60 Hz |
| Original sample count | 1,000 | 50, 100, 200, 1,000, and 10,000 |

The article input comment says energization occurs at 10 ms, but switch cards
and ATP output use a 20 ms mean. The executable cards, not the comment, define
the experiment.

The article also combines 50 Hz sources with a common reference-angle delay
defined at 60 Hz. Its 0-360 degree delay therefore spans 16.667 ms, not the
20 ms source period. The project case uses 60 Hz consistently.

## Statistical request differences

Both cases use the same core ATP/GTPPLOT method:

- normal independent switching-time perturbations;
- one absolute peak per variable and energization;
- `MODTAB = 3`, producing individual and grouped tables;
- fixed `AINCR = 0.05 p.u.` compartments;
- ATP frequency, cumulative-frequency, and exceedance columns.

The monitored spaces differ substantially.

The article requests only three receiving-end phase-ground voltages,
`FASEA2`, `FASEB2`, and `FASEC2`, plus one phase-phase branch voltage
`FASEA2-FASEB2`. ATP produces five distributions: three node distributions,
one maximum-of-three node `SUMMARY`, and one branch distribution.

The project ATP source requests three phases at `T_MAN`, `1_2LT`, and `T_OPO`,
plus three phase-phase voltages at each position and grouped summaries. It
produces 24 distributions. The current analysis pipeline intentionally selects
only phase-A phase-ground peaks at the three positions.

## Result comparison at 1,000 energizations

The closest conceptual comparison is article receiving-end phase A against
project remote-terminal phase A. They are not the same electrical system.

| Metric | Article `FASEA2` | Project `T_OPOA` |
|---|---:|---:|
| Mean (p.u.) | 1.7833 | 1.6949 |
| Sample standard deviation (p.u.) | 0.3316 | 0.1390 |
| Maximum represented by source bins (p.u.) | up to 2.70 | up to 1.90 |
| Empirical `P(X > 2.3 p.u.)` | 8.5% | 0% |

The article distribution is much wider and has a materially heavier upper
tail. This difference is expected from topology, terminal conditions,
frequency, switch dispersion, simulation window, protection equipment, and
different p.u. bases. It does not indicate an error in the new histograms.

The same 2.3 p.u. threshold means 230.0 kV in the article phase-ground table
and 259.16 kV in the project phase-ground tables. Direct percentage comparison
therefore answers a normalized question, not an equal-physical-voltage
question.

Article source results at 2.3 p.u. are:

| Article variable | Mean (p.u.) | Standard deviation | `P(X > 2.3)` |
|---|---:|---:|---:|
| `FASEA2` | 1.7833 | 0.3316 | 8.5% |
| `FASEB2` | 1.7981 | 0.3244 | 6.8% |
| `FASEC2` | 1.8537 | 0.3325 | 11.4% |
| Maximum of phases | 2.1347 | 0.2332 | 26.5% |
| Branch `FASEA2-FASEB2` | 2.7049 | 0.3870 | 84.3% |

The branch percentage must not be compared with phase-ground percentages.
The article uses the same 100 kV base for its node and branch tables, whereas
the project explicitly separates 112.677 kV phase-ground and 195.161 kV
phase-phase bases.

## Invalid existing processed result

`coisas/results/artigo-1000` is not a valid processed representation of the
original article case:

1. Its configuration points to `padronizado-100`, declares only 100 samples,
   and names output directory `results/artigo-100`.
2. Its metadata confirms 300 raw rows, 100 analyzed rows, and one summary row.
3. Its stored input path no longer matches the current `coisas/` location.
4. It was generated by an older parser that mixed node and branch variables.

For simulation 1 of `padronizado-100`, the LIS node phase-A magnitude is
2.29849 p.u., while branch A-B magnitude is 2.86642 p.u. The CSV stores
`terminal=FASE2, phase=A, value_pu=2.86642`. Consequently, its reported phase-A
mean of 2.6754 p.u. is actually dominated by the phase-phase branch variable.
That summary and its 77% exceedance result must not be cited as phase-ground
article evidence.

Current parser behavior can extract 1,000 node observations per phase from the
standardized 1,000-run file. A defensible article comparison should regenerate
artifacts with explicit source lineage and distinct node/branch identities,
then validate direct observations against the original ATP frequency tables.

## Interpretation

The article validates the tabulation and plotting method, not the expected
shape or voltage level of the project distributions. Matching the article
requires equal bin semantics and probability definitions. Matching its
histogram shape would be scientifically unexpected because the modeled
electrical systems and experiment distributions are different.

