# Scientific validation status review

Assessment date: 2026-09-07.

## Subsequent validation

On 2026-09-08, TCCKL-8 was promoted to `Concluído` after the parser was
checked against independently transcribed records from five real ATP files and
all 235 primary statistical files were scanned successfully. See the
[parser validation report](parser_validation_report.md). The remaining table
and conclusions below preserve the scope of the original 2026-09-07 review.

## Decision and scope

The [task index](../afazeres/README.md) now distinguishes Concluído,
Validando, and Pendente. All 12 previously completed cards moved to
`afazeres/validando/`; the eight pending deliverables remain pending.
Concluído is reserved for delivery with documented scientific acceptance
within the item's declared thesis scope. No such completed validation record
was identified for these 12 items in the reviewed material.

This is an evidence-based workflow assessment, not a finding that every
implementation is scientifically wrong. Supporting software tasks can be
accepted through documented fidelity, requirement verification, and
reproduction checks; they need not independently validate downstream models.
A hypothesis rejected by a documented study can still be a completed task.

The review inspected source implementations, test definitions, the existing
cards, active thesis chapters, and the five saved result packages. It did not
rerun software tests, ATP simulations, or LaTeX compilation, and it did not
perform scientific validation or independently verify bibliography contents.
Earlier reports of 94 passing tests, 95% coverage, or a 36-page PDF remain
historical claims, not fresh verification results. Earlier estimates of about
65% completion do not measure the stricter scientific acceptance criterion.

## Repository and thesis evidence

| Cards | Implementation evidence | Missing acceptance evidence |
| --- | --- | --- |
| 01–02 | `src/parser/`, `src/services/preprocessing.py`, parser and preprocessing tests | Independent source-to-table audit, completeness, and declared observation scope |
| 03 | `extract_maxima_dataframe` computes `abs(value) / base_voltage` | Documented electrical base and independently checked conversions |
| 04 | `src/services/validation.py` checks schema, identities, finite values, and selection | Experimental integrity rules, exclusions, and their validation |
| 05–06 | `src/services/statistics.py` computes sample statistics and Normal survival probabilities | Distribution diagnostics, uncertainty, and effect of prior filtering |
| 07–08 | `src/services/clustering.py` and `comparison.py` produce labels and candidate signals | Parameter justification, stability, and independent technical reference |
| 09 | `src/services/reporting.py` saves CSVs, figures, configuration, hashes, and library versions | Recorded reproduction of final results and links to thesis outputs |
| 10 | Five saved packages under `input_files/casos/` | Sample generation provenance, convergence analysis, and final matrix coverage |
| 11 | `tests/` and checks configured in `pyproject.toml` | Dated final-revision verification mapped to scientific requirements |
| 12 | `doc/main.tex` has introduction, theory, and electrical-system modeling | Recorded scientific review and consistency with final methodology/results |

The active chapters in [main.tex](main.tex) are Introduction, Theoretical
Foundation, and Electrical-System Modeling. Methodology and Results/Discussion
are not implemented as chapters; the Conclusion chapter is commented out.
The introduction already describes voltage maxima, and the modeling chapter
explains the table extraction. Accordingly, the review does not assume that
all current prose incorrectly promises waveform clustering. The older card's
blanket wording about “wave behaviors” needed qualification.

Two specific consistency checks remain:

- `main.tex` describes a 138 kV line, whereas all five configurations use
  `base_voltage = 100000.0`. This difference alone does not establish an error:
  units and phase/line and RMS/peak conventions must be reconciled explicitly.
- The DBSCAN discussion says noise should not be discarded automatically.
  `run_pipeline` calls `filter_valid_events` before `summarize_statistics` and
  Gaussian fitting. The methodological decision and its effect therefore need
  validation. Original observations and candidate annotations are still saved.

## Saved artifact checks

The following counts were read from `annotated_observations.csv` and checked
against the counts in `metadata.json`. Raw counts below are metadata counts;
annotated, noise, and candidate counts were computed from the annotated CSVs.
These are saved results, not newly executed experiments.

| Simulations | Raw rows | Annotated rows | DBSCAN noise | Candidate rows |
| ---: | ---: | ---: | ---: | ---: |
| 50 | 450 | 150 | 0 | 78 |
| 100 | 900 | 300 | 0 | 164 |
| 200 | 1,800 | 600 | 0 | 322 |
| 1,000 | 9,000 | 3,000 | 0 | 1,592 |
| 10,000 | 90,000 | 30,000 | 0 | 16,156 |

All five `input.json` files select phase A, three terminals, and the
`T_MAN/SRPI/CASO-COMPLETO/SDEF` scenario. They use `eps = 3.0`,
`min_samples = 2`, two K-Means clusters, seed 42, and threshold 2.3 P.U.
Raw extraction includes phases before selection; the smaller annotated counts
refer to the selected phase, not the total raw table.

DBSCAN runs per terminal on `value_pu`; K-Means runs on that single feature
across the selected terminals. The candidate rule counts highest-centroid
membership as one signal and accepts any signal. These facts explain why a
candidate label cannot be treated as an independently validated numerical
error. Candidate proportions in the saved files range from 52% to about 55%.

## Acceptance record and maintenance

Each moved card now has its own unchecked evidence checklist and links to
related pending studies. Promotion requires a validation date, reviewer,
evaluated scope, source/configuration/code provenance, procedure and reference,
results, limitations, acceptance decision, and thesis location. Any technical
review needed for physical interpretation must be recorded, not inferred from
software test success.

The existing Portuguese assessment bodies were retained as historical context;
new explanatory documentation is in English according to AGENTS.md, while the
three requested category labels retain their Portuguese names. The referenced
RTK.md was not found in the repository root or the checked parent/configuration
locations, so no additional instructions from that file were available.

Only task documentation and this review were changed. Link resolution, card
counts, and the absence of stale `concluido/` card references were checked
locally. No scientific acceptance was granted by this reorganization.
