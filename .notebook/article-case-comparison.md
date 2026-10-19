# Article Case Comparison
> GTPPLOT method matches; electrical experiments do not

Entry: `coisas/inputs/artigo/original/2000-N4-Statis.lis`

Article case:
- 1,000 runs; 100 km; 50 Hz sources; 20 us step; 50 ms end
- 10 nodes, 3 branches, 3 sources, no nonlinear elements
- Switch mean 20 ms, sigma 1 ms; common 0-360 degree delay at 60 Hz
- Base 100 kV for both node and branch tables
- 3 receiving-end node phases + one A-B branch; five distributions

Project SRPI 1,000:
- 80 km segmented line; 60 Hz; 10 us step; 300 ms end
- 100 nodes, 144 branches, 9 sources, 18 nonlinear elements
- Switch mean 20 ms, sigma 0.833 ms
- 112.677 kV phase-ground; 195.161 kV phase-phase
- 24 ATP distributions; pipeline selects phase-A nodes at 3 positions

Gotcha: `coisas/results/artigo-1000` actually processes 100 runs and older
parser stores A-B branch magnitude as phase A. Do not cite its summary.

Details: `doc/article_case_vs_project_cases.md`

Probability protocol:
`doc/probability_experiment_prerequisites.md`
- Article reproduction and SRPI probability are separate experiments
- Histogram similarity is not an estimator-validity criterion
- 10,000 zero events -> two-sided 95% Wilson upper bound 0.0384%

Updated: 2026-10-07
