# Defense evidence v10: clustering-only candidate selection

## Current scope

The latest explicit user instruction removes MAD from active v10 measures
and selection. Candidate evidence now comes exclusively from K-Means
centroid distance, DBSCAN noise and hierarchical upper-tail separation.
Silhouette and Davies–Bouldin remain the primary partition validation
metrics. Descriptive statistics and empirical exceedance are supplementary;
none establishes the physical or numerical cause of an observation.

## Implementation

The existing one-dimensional single-linkage hierarchical rule and fitted
clustering parameters remain unchanged. The pipeline no longer computes
MAD columns, its configuration no longer accepts `mad_threshold`, and
comparison/convergence/technical-review artifacts no longer consume MAD.
The standalone MAD helper remains isolated for historical compatibility;
it has no role in the published analysis. Gaussian adequacy remains
separate and original switching parameters remain unchanged.

The same v10 package is regenerated under explicit user authorization.
Historical v9 remains preserved. Generator version is 2.1.0; the method
policy is `defense-v10-clustering-methods`. Candidate reasons are
`kmeans_distance;dbscan_noise;hierarchical_upper_tail` where applicable.

## Publication and reproduction

The thesis includes K-Means, DBSCAN and hierarchical `*_clusters.png`
figures from CRPI, N=200, phase A. The three documents contain no MAD
criterion, formula or discussion. Presentation remains 16 slides/20 minutes.

`just build-v10 --overwrite` regenerates v10, copies referenced standalone
assets and compiles thesis/slides/notes. Without `--overwrite`, nonempty
packages are protected. `just build` and `just build-presentation` compile
already prepared assets.

## Expected numerical change and final checks

Applying the three clustering flags gives 2,010 candidates. Hierarchical
selection flags 29 observations, eight unique to that criterion. Reference
T_OPO, phase A, N=10,000 has 99 candidates (0.99%) in each scenario.
These totals must be verified against fresh v10 outputs before completion.
Geometric metrics are expected to remain unchanged because partition
algorithms and parameters did not change. Final test, hash and compilation
results are recorded in the feature task status.

## Completed verification

Fresh outputs confirm 204,300 retained observations, 2,010 candidates,
29 hierarchical selections (eight unique), and 99 reference candidates
per scenario. Every generated CSV was checked for absence of MAD columns.
All 609 output hashes match the 2.1.0 manifest; all 270 geometric metric
records match historical v9, as expected from unchanged cluster fitting.
Full suite:344passed; independent generator/copier tests:9passed; format,
lint and types clean. Thesis88pages, slides16, notes10 compile without
warnings or overflow. The revised candidate table was visually inspected.
