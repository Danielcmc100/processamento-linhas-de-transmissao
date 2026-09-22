# Project State

**Updated:** 2026-09-22

## Decisions

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
  pipeline through parsing, cleaning, DBSCAN, K-Means, sigma comparison,
  summaries, and plots.
- The artifact writer produces seven auditable outputs with deterministic
  tables/configuration, input hashes, counts, software versions, and an
  explicit overwrite policy.
- The implementation and quality-gate evidence are documented in
  `doc/validation-evidence.md`.
- Parser fidelity is accepted for the audited real ATP layouts. The evidence
  covers 235 primary files, 533,450 runs, and independently transcribed
  checkpoints in `doc/parser_validation_report.md`.

## Next actions

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
