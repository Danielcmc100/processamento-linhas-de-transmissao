# Thesis readability additions

Date: 2026-11-02.

## Scope

The first stage applied the high-priority recommendations. Its figure,
table, and page numbers below describe the first-stage PDF; see the final
stage for the current document.

Applied the five high-priority recommendations to `doc/main.tex`:

- Figure 9: one ATP execution produces nine terminal/phase observations.
- Table 2: four validity layers, evidence, and interpretation limits.
- Table 3: detector rules, applicability, and voting roles.
- Table 6: candidate counts, rates, intersection, and union.
- Figure 16: benchmark precision and recall by intervention and contamination.
  Table 7 supplements the figure with false positives in the clean control,
  where recall is undefined.

Surrounding prose now refers to the summaries. Hierarchical labels remain
descriptive and non-voting; Gaussian adequacy remains separate from detection.
No experimental results were regenerated.

## Saved data and reproduction

`doc/illustrations/benchmark.csv` is an exact copy of
`results/defense-evidence/v9/tables/benchmark.csv`. Both have SHA-256:

```text
0c7a60fabbc618fd54a1c08c7a7271694ac822a6c61dcecee34b2b7e1ebbb9ba
```

Render the vector figure and compile the self-contained thesis:

```bash
uv run python -m docs.research.render_thesis_readability_figures
just build
```

The annotated observations confirm that all 204,300 records use DBSCAN
`effective_eps=0.5`, `min_samples=5`, and
`parameter_source=explicit_effective_eps`. The methodology previously claimed
95th-percentile radius calibration. Its description and the new method table
now match the saved configuration. Production code and evidence are unchanged.

## Verification

- Candidate summary checked against `sources/annotated_observations.csv`:
  CRPI MAD/union 109; SRPI MAD/union 852; K-Means/intersection 99 in each;
  DBSCAN zero in each. All three detectors applicable to all 10,000 records
  per reference group.
- All 18 intervention rows' saved precision and recall agree with their
  confusion counts. Clean controls retain 42 and 391 false positives.
- Ruff check, Ruff format check, and focused BasedPyright check passed.
- `just build` passed; final PDF has 83 physical pages. Final LaTeX log has
  no undefined references or overfull/underfull box warnings.
- Rendered and visually inspected the complete new-item pages: physical
  PDF pages 38, 41, 43, 57, 60, and 61 (printed 37, 40, 42, 56, 59, 60).
  Checked labels, table spacing, arrows, axes, coincident recall curves,
  captions, and sources. No clipping or overlap found.
- Existing unrelated working-tree edits were preserved. No commit created.

## Remaining recommendations: final stage

Applied the remaining five visual recommendations in `doc/main.tex`:

| Addition | Current label | Printed page |
| --- | --- | --- |
| Annotated illustrative boxplot | Figure 2 | 22 |
| Integrity and cleaning decisions | Table 2 | 39 |
| Dataset composition by sample size | Table 3 | 40 |
| Controlled evaluation workflow | Figure 11 | 45 |
| CRPI/SRPI reference-group statistics | Table 7 | 50 |

The boxplot uses native TikZ and clearly separates theoretical fences,
observed whisker endpoints, and exterior points. It is illustrative and
does not add IQR to the implemented detector votes. The workflow uses native
TikZ and shows source/run splitting before copied-data interventions, fitting
on development only, and evaluation with frozen parameters. Its behavior was
checked against `src/services/controlled_benchmark_runner.py`.

The normalization discussion now has its own numbered section, preserving
`sec:per-unit-validation`. The theory now presents the Wilson interval used
in the experiment instead of the symmetric Wald approximation, and explains
its positive upper bound for zero observed events. No statistical computation
or experiment changed. Float barriers keep the new summaries before the next
discussion and prevent their placement inside following paragraphs.

Final verification:

- Counted saved annotated observations by scenario and sample size: each
  file has exactly `9 * N` records; each scenario has 102,150 records;
  total is 204,300 across ten files and ninety groups.
- All displayed reference-group statistics match the saved
  `sources/distribution_adequacy.csv` values at the displayed precision.
- For zero events, the Wilson expression gives upper bounds 0.0713,
  0.0370, 0.0188, 0.0038, and 0.0004 at the five sample sizes, matching
  the existing probability tables.
- `just build` passed. Final PDF has 85 physical pages, with no undefined
  references or overfull/underfull box warnings in the final LaTeX log.
- Visually inspected complete rendered physical pages 23, 24, 38, 39, 40,
  41, 46, 50, and 51. Corrected an initial workflow overlap; final nodes,
  arrows, captions, equations, and table cells are legible and unobstructed.
- `git diff --check` passed for the changed manuscript and validation note.
  No Python or production code changed in this final stage.
