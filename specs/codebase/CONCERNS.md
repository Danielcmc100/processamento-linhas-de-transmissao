# Concerns

## High priority

- **Type gate failure:** Matplotlib stub incompatibilities or overly narrow
  annotations in `visualization.py` produce six BasedPyright errors.
- **Reproducibility:** `main.py` hard-codes an absolute directory, phase,
  voltage base, DBSCAN parameters, and output filenames.
- **Data evidence:** tests use synthetic text only; no real ATP fixture checks
  malformed sections, encoding variation, missing maxima, or file-level
  aggregation.

## Methodological

- A DBSCAN label of `-1` is an algorithmic noise label, not a demonstrated ATP
  numerical error. The TCC must state the evidence and limitations clearly.
- Gaussian fitting currently uses sample standard deviation but does not test
  normality, confidence intervals, goodness of fit, or uncertainty of tail
  estimates.
- K-Means exists as a service but is not used by the end-to-end script and is
  not covered by tests.
- The current pipeline filters to one phase, so phase comparison is not yet a
  delivered result.

