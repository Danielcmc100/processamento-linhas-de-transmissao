# Multiple hierarchical groups: potential benefit

Analysis date: 2026-10-05.

The inspected `cluster_hierarchical()` has no cluster-count parameter.
It returns binary reference/upper-tail membership by selecting one eligible
gap per terminal. Current defaults are `min_gap_pu=0.03`, `gap_factor=1.0`,
and `max_tail_fraction=0.1`; earlier analyses used different defaults.
`kmeans.n_clusters` in the case input configuration does not control this
hierarchical rule.

Additional descriptive groups could expose intermediate voltage bands or
multiple separated upper subsets. This may help characterize distributions
and prioritize review, but more groups do not by themselves improve extreme
detection or establish distinct physical regimes. Forcing a fixed group
count can split a continuous distribution without meaningful separation.

For the original goal of distinguishing a reference population from a
separated upper tail, retain binary membership. If additional structure is
needed, add separate descriptive group IDs obtained from multiple qualifying
gaps, while preserving the independent upper-tail selection criterion.
The number of groups should follow supported separation rather than a
required count of three or four. Low- and high-voltage descriptive groups
must not automatically become anomaly flags.

Evaluate any extension by comparing selected observation identities,
boundary gaps, group sizes, and resampling/parameter stability within
comparable scenario-terminal-phase-source groups. Independent controlled
evaluation is needed before claiming improved detection. The existing
binary Patito label schema would need a separate schema/column for general
group IDs; widening its allowed range alone would change its meaning.

No clustering code or result artifacts were modified for this assessment.
