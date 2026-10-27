# Project State

**Updated:** 2026-10-27

## Decisions

- 2026-10-27: The author authorized the next four readability tasks in
  canonical dependency order: T1, T3, T4 and T5. Each was implemented by a
  distinct sequential sub-agent, using local filesystem/shell tools.

- 2026-10-26: The author clarified that three sigma belongs to the modeled
  statistical circuit breaker, not to a voltage anomaly detector. T7.1–T7.5
  in `specs/features/thesis-readability-and-sigma-correction/` retire the
  latter and are verified. Raw ATP switching settings and historical
  evidence are preserved; earlier voltage-sigma requirements are superseded.
- 2026-10-26: Figure/table review is recorded in
  `docs/research/thesis_visual_editorial_review.md`; the same feature plan
  includes condition/source identity corrections, table compression, chart
  coherence and final rendered-PDF verification.
- The academic scope ends at validated data analysis; automated insulation
  optimization remains outside the TCC.
- Each configured run analyzes one explicit phase to avoid mixing phase
  distributions.
- DBSCAN noise is treated as a candidate anomaly, not definitive proof of a
  numerical ATP error.
- Existing code and project documentation are written in English where the
  repository conventions require it; the TCC manuscript remains in Portuguese.

## Blockers and risks

- Technical/electrical review of flagged candidates remains unresolved:
  waveforms, repeat simulations with a reduced integration step, and a
  qualified independent electrical reviewer were never available. This is
  declared explicitly in `results/defense-evidence/v1/package_status.json`
  (`package_status: "incomplete"`, `causal_conclusion: "unresolved"`) and in
  `doc/main.tex`'s Conclusão — it is not silently omitted.
- DEF-26 (repeat-simulation numerical sensitivity via a reduced ATP
  integration step) is Blocked: it requires the ATP solver itself, which has
  no runtime available in this environment. See
  `specs/features/thesis-defense-evidence/validation.md`.

## Completed software capability

- READ-01/03/04/05: consolidated limitations, relocated audit logistics to
  the appendix, separated theory paragraph roles and standardized terms,
  acronym first uses and source-lineage semantics. T1 `ac16319`, T3
  `f0467e5`, T4 `1a13400`; T5 is recorded with the terminology commit.
  The current manuscript builds to 80 pages with affected-page visual review;
  citations, inclusions, graphics, equations and labels are preserved.
  Taskipy format/lint pass and 327 tests pass. Detailed task evidence:
  `docs/research/thesis_readability_validation.md`.

- READ-07: comparison uses applicable MAD, K-Means distance and DBSCAN noise
  only. Sigma thresholds, votes and overlays are retired; descriptive and
  Gaussian adequacy computations remain. Evidence v3 includes 204,300
  observations from ten sources, 13,716 candidates and 13,708 disagreements.
  All 609 output hashes and 3,743 preserved input/historical file hashes
  were checked. Final Taskipy suite: 327 passed; format/lint/typecheck pass.
  Manuscript builds to 80 pages; affected prose and assets were visually
  reviewed. Full proof: `docs/research/thesis_sigma_correction_validation.md`.
- T7.1–T7.4 are committed (`81b633b`, `661f791`, `acd458d`, `3d3d3ce`).
  T7.5 and task tracking are recorded with the manuscript commit after the
  author authorized retrying the initially interrupted staging operation.
  Generated v3 results are Git-ignored; referenced manuscript assets are
  versioned under `doc/evidence/v3/`.
- The Thesis Defense Evidence Package feature
  (`specs/features/thesis-defense-evidence/`) is complete: 26 of 27
  requirements Verified, 269 tests passing (up from a 112 baseline), 0
  lint/typecheck errors, and a clean 62-page LaTeX build. Full gate results
  and requirement traceability are in
  `specs/features/thesis-defense-evidence/validation.md`.
- The evidence pipeline computes, for the ten declared SRPI/CRPI ATP
  sources: descriptive/probabilistic statistics with Wilson confidence
  intervals, Gaussian adequacy (Anderson-Darling) with a robust MAD
  baseline, contextual K-Means and calibrated DBSCAN candidate evidence,
  explicit method comparison, a controlled synthetic-perturbation benchmark,
  cross-sample-size convergence, and parameter-sensitivity/stability
  evidence — all reproducible from `scripts/build_defense_evidence.py` into
  `results/defense-evidence/v1/` with a signed reproducibility manifest.
- The controlled benchmark and parameter-sensitivity replay now run
  successfully against the real target data (previously blocked by a crash
  in `controlled_benchmark_runner.py` fixed during T20 verification — see
  validation.md).
- A validated JSON configuration drives a machine-independent, single-phase
  pipeline through parsing, cleaning, DBSCAN, K-Means, three-method comparison,
  summaries, and plots.
- The artifact writer produces seven auditable outputs with deterministic
  tables/configuration, input hashes, counts, software versions, and an
  explicit overwrite policy.
- The implementation and quality-gate evidence are documented in
  `docs/research/validation-evidence.md`.
- Parser fidelity is accepted for the audited real ATP layouts. The evidence
  covers 235 primary files, 533,450 runs, and independently transcribed
  checkpoints in `docs/research/parser_validation_report.md`.

## Next actions

- Continue readability tasks in canonical order: T6 → T9 → T2 → T8,
  followed by T10–T12. T1, T3, T4, T5 and T7 are verified; final
  whole-document layout acceptance remains assigned to T12.
- Obtain waveform data, repeat-simulation evidence, and a qualified
  independent electrical reviewer to close the technical review and move
  the causal conclusion out of "unresolved" — this is now the only
  remaining gap before the evidence package can be marked fully complete.
- No further software work is required by the thesis-defense-evidence spec;
  remaining work is domain/data acquisition (electrical review), not code.

## Preferences

- Lightweight bookkeeping tasks (state updates, validation write-ups) work
  fine on a cheaper/faster model; worth defaulting to that for similar
  session-closing work.

## Deferred ideas

- Automated insulation-level recommendation (permanently out of academic
  scope; protects partner-company IP, per AGENTS.md).
- Company expert-system logic (same).
- Automatic causal labeling of ATP numerical errors (same).
- Repeat ATP simulation with a reduced integration step, once an ATP
  runtime is available (DEF-26, currently Blocked).
- Oral-defense slide deck.
