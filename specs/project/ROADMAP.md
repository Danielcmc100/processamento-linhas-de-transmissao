# Roadmap

## M1 — Baseline implementation (complete)

- [x] Parse the ATP statistical `.lis` structure.
- [x] Normalize phase-to-ground maxima to P.U.
- [x] Fit Gaussian summaries and calculate exceedance probabilities.
- [x] Provide DBSCAN, K-Means, and visualization primitives.
- [x] Add unit tests for the main isolated services.
- [x] Resolve type-checking errors in visualization code.

## M2 — Research-grade validation

- [ ] Validate parsing against representative real ATP outputs.
- [x] Make input, phase, voltage base, terminals, and model parameters
  configurable.
- [x] Add integration tests for the full pipeline.
- [x] Compare statistical and clustering classifications with explicit rules.
- [x] Document limitations and evidence for interpreting anomalies as numerical
  artifacts versus physical events.
- [ ] Validate Gaussian assumptions, clustering parameters, and anomaly
  interpretations on the target dataset with domain review.

## M3 — TCC evidence package

- [x] Provide infrastructure for reproducible tables and figures, verified with
  a documented representative synthetic fixture.
- [x] Record sample counts, parameters, input hashes, and run metadata.
- [ ] Produce and interpret the actual TCC results from the target dataset.
- [ ] Align target-dataset outputs with the methodology and results chapters.
