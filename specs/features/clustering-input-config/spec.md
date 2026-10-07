# Clustering input configuration

## Goal

An analysis run can set K-Means and hierarchical separation parameters in
the same input JSON, and the saved configuration records effective values.

## Requirements

| ID | Requirement | Verification | Status |
| --- | --- | --- | --- |
| CIC-01 | K-Means uses `n_clusters` and `random_state` from `kmeans`. | Pipeline parameter test | Verified |
| CIC-02 | Hierarchical labels use `min_gap_pu`, `gap_factor`, and `max_tail_fraction` from `hierarchical`. | Pipeline parameter test | Verified |
| CIC-03 | Invalid hierarchical parameters fail configuration validation. | Configuration boundary tests | Verified |
| CIC-04 | Input files and saved configuration expose effective parameters. | Input JSON validation and serialization test | Verified |

Existing input JSON files without `hierarchical` remain valid through the
documented defaults. Cluster activation, algorithms, and the separate Ward
dendrogram are outside this change.
