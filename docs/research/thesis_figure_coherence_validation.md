# Thesis Figure Coherence Validation

## T10.1 — Conceptual and electrical-model figures (2026-10-28)

Status: complete. Scope: READ-10 conceptual/model figures and TODOS REQ-04.
The author authorized sequential sub-agent implementation using local tools.
No Python code, scientific evidence package, experiment, raw input or image
asset changed. Existing changes in TODOS.md and staged/unstaged tasks.md were
not included in this task.

### Ownership and preservation

The previous `imagens/fluxo.png` overview was assessed directly: it described
`.OUT` output, omitted the implemented validation/analysis layers and repeated
an overview outside methodology. Its inclusion was replaced, its original
bytes retained. Exactly one `fig:fluxograma_atp` definition now owns the
implemented workflow near the opening of `chap:methodology`. Theory points
forward through automatic references. Existing TikZ supplies vector text and
arrows; local skill-directory search found no mermaid-studio installation.
No second diagram framework or dependency was introduced.

The retained illustrations have distinct purposes:

| Stable label | Purpose | Physical PDF page / printed page |
| --- | --- | --- |
| `fig:linha_colqui` | Cited example of a transient line model, not this experiment | 22 / 21 |
| `fig:nuvem-clusters-anomalias` | Point positions and centroid concept | 24 / 23 |
| `fig:kmeans-mahon` | Effect of separation in synthetic groups | 28 / 27 |
| `fig:dbscan-comparacao` | Density versus proximity in synthetic spatial examples | 29 / 28 |
| `fig:equivalente_anafas` | Reduced-network provenance | 32 / 31 |
| `fig:equivalente_atp_draw` | Implementation of that network in ATPDraw | 34 / 33 |
| `fig:modelo_linha` | Actual segment lengths and monitoring positions | 35 / 34 |
| `fig:fluxograma_atp` | Authoritative processing overview | 36 / 35 |

The theoretical examples explicitly describe their two-dimensional,
illustrative nature, distinct purposes and lack of evidential force for the
actual one-dimensional per-terminal/per-phase maximum-voltage analysis.
Thus none is presented as an additional implemented experimental method.
The three electrical-model images remain complementary. ANAFAS/ATPDraw
images use full text width with readable vector legends repeating the bus
identifiers discussed in the prose. The line figure adds a native TikZ inset
showing existing 13.3/26.7/26.7/13.3 km segments and T_MAN/1_2LT/T_OPO
positions, with Portuguese displayed decimals. It introduces no new network
parameter or simulated outcome. Original raster detail remains available in
preserved source assets.

### Semantic checks

The overview includes ATP generation separately from Python processing;
`.lis` input; maximum/time extraction; source/scenario/run/terminal/phase
identity; P.U. conversion; integrity and logged deterministic exclusions;
mean and sample standard deviation; empirical exceedance and Wilson interval;
Gaussian adequacy and its qualified comparison; MAD, K-Means distance and
DBSCAN noise under applicability; descriptive non-voting hierarchical labels;
method/sample-size comparison; controlled synthetic evaluation; sensitivity;
and reproducible outputs. The final dashed box and arrow explicitly identify
pending qualified electrical review and unresolved causal status.
`SIGMAX=3.0` appears only as input switching configuration. Gaussian adequacy
is separated visually and explicitly excluded from detection voting.

The methods and units agree with the existing methodology descriptions and
the accepted project invariants. No claim of verified numerical ATP errors,
automatic physical classification or completed electrical review was added.
Comparison against HEAD confirmed all 44 citation commands and all 14 figure
label definitions preserved (including moved labels), with one workflow label.
`git diff --name-only HEAD -- doc/imagens` returned no changed assets.

### Gates and rendered review

- `just build`: pass; 81-page PDF. Log contains no undefined references or
  citations, multiply-defined labels, missing assets, or overfull boxes.
- `uv run task format`: pass; 172 files unchanged.
- `uv run task lint`: pass.
- Parent-run fresh `uv run task test` baseline: 328 passed in 76.72 seconds.
  No software changed in T10.1; software/publication gates are not required
  by its editorial gate definition.
- `git diff --check`: pass.
- Poppler rendered and visual inspection completed for physical PDF pages
  22, 24, 28, 29, 32, 34, 35 and 36, at 1200–1400 pixels per page.
  Captions, sources, electrical legends and new vector diagram were checked
  for clipping, readable text and arrows, scope, interpretation and references.
  The methodology overview fits on its opening page together with its
  introduction; no duplicate overview remains in theory.

Whole-document float integration and residual paragraph splits remain T12.
In particular, the existing floating line-model figure can interrupt the
following model-description paragraph. This task does not claim final layout
acceptance, nor change the pending T10.2–T10.4 statistical figures.
