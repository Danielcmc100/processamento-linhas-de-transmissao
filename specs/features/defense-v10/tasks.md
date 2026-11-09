# Execution and verification: clustering-only v10 revision

- [x] T1 (R1–R2): Remove active MAD computation/configuration/evidence,
  preserve explicit three-clustering criteria and regression coverage.
- [x] T2 (R4): Update generator 2.1.0 and policy; reject MAD output columns
  in the scientific orchestration regression test.
- [x] T3 (R3,R5): Revise current scientific documents, remove MAD references,
  preserve partition validation metrics and three cluster figures.
- [x] T4 (R4,R6): Regenerate and verify 204,300 real observations, new
  candidate totals, scientific output hashes and unchanged partition metrics.
- [x] T5 (R1–R6): Verify format/lint/types/tests, compile all documents and
  inspect changed candidate table/representative presentation.

No unrelated staged user changes will be committed by this task.

Final proof: 344 full-suite tests passed, nine generator/copier tests
passed independently, Taskipy format/lint clean, BasedPyright zero errors
or warnings. Regenerated 204,300 observations contain no MAD columns.
All 609 output hashes verified; 270 partition metric records unchanged.
Candidate union: 2,010; hierarchy: 29, eight unique. Reference: 99 each
scenario. Thesis88pages/slides16/notes10 compiled with no warnings or
overflow; candidate-table page rendered and visually inspected.
