# Final thesis editorial integration validation

## T13 — Consolidated final discussion (2026-10-28)

Status: complete. Editorial-only change; no software, generated evidence,
raw input, or template asset changed. The author authorized sequential
sub-agent execution of the remaining queue with local filesystem tools.

### Source inventory and preservation

The original final results block contained three sections, identified by
`sec:avaliacao-controlada`, `sec:discussao-resultados`, and
`sec:alcance-limitacoes`, plus subsection `sec:lacunas-pacote`.
It is now one section titled exactly `Discussão acerca dos resultados`.
All four unique labels remain aliases of this section, so introduction and
conclusion references continue to resolve. Internal forward/self references
were replaced by transitions; no duplicate or undefined label was introduced.

The connected paragraph order preserves the following original claims:

- Controlled evaluation: CRPI/SRPI reference group, T_OPO, phase A, 10,000
  simulations and execution-block development/evaluation split; three
  intervention families, 1%, 5%, 10% contamination and clean baseline;
  42/5,400 versus 391/5,400 false positives (0.0078/0.0724); contextual
  recall 1.0000, F1 ranges 0.7200–0.9660 and 0.2173–0.7531; point/collective
  precision-recall tradeoffs. Contamination and intensity remain distinct.
  Table `tab:defesa-benchmark` and appendix `app:benchmark-detalhado`
  references remain present. Scope stays restricted to tested synthetic
  conditions and the evaluated group, without claiming real ATP-error accuracy.
- Sensitivity: frozen K-Means/DBSCAN grid; twenty applicable replicas, ten
  per method and five per scenario, Jaccard 1.0000 against threshold 0.80.
  Parameter stability remains reproducibility evidence, not detection accuracy.
- Review: five cases covering agreement, disagreement, high score and
  unsignaled control; all remain causally unresolved. Table
  `tab:defesa-revisao-tecnica` and appendix `app:casos-revisao-pendente`
  retain source identity, voltage, analytical evidence and full-path/hash mapping.
- Objectives: extraction, organization, statistics, probability, clustering,
  comparative candidate evidence and reproducible integrated pipeline remain
  computational accomplishments. Ten declared files and manifest remain cited.
- Limits: maxima do not represent waveforms, duration, frequency, rate of
  change or oscillatory content; conclusions cover the declared sources and
  validity layers. Package status remains incomplete. Waveforms, smaller-step
  repeats and independent qualified electrical review are absent. No new ATP
  simulation or waveform audit occurred. MAD/K-Means/DBSCAN, rarity, geometry,
  agreement and selection stability cannot establish numerical or physical
  cause. Future causal validation still requires origin, switching conditions,
  interphase/interterminal coherence and missing electrical evidence.

Repeated synthetic-scope and stability-versus-accuracy caveats in the old
objectives paragraph were consolidated into their earlier benchmark and
sensitivity paragraphs. No numerical result, citation, figure, table, or
substantive caveat was removed.

### Editorial gate and visual proof

- `rtk just build`: passes; final PDF has 84 pages. The final log has no
  unresolved references/citations, multiply defined labels, missing assets,
  overfull boxes or underfull boxes.
- Source assertions: exactly one section and no subsection/deeper heading in
  the merged block; four label aliases each occur once; all document labels
  remain unique.
- `pdftotext -layout doc/build/main.pdf /tmp/t13.txt` confirms the contents
  entry and section 5.8 use the requested title; conclusion references resolve
  to 5.8.
- Rendered physical PDF pages 60–63 (printed pages 59–62) were inspected using
  `pdftoppm -scale-to 1400 -png` and image viewing: complete discussion,
  continuation, and conclusion boundary are readable without clipping or
  stranded headings. The short final discussion page is a chapter boundary,
  not a newly forced float/page break. Whole-document layout remains T12.

No SPEC_DEVIATION. Tracking and commits belong to the orchestrating agent.
