# Documentation and thesis builds

`doc/` is the single, standalone thesis source directory. It contains only
compilation inputs and preserved template assets. The root `justfile`
provides build commands. Generated outputs stay in its ignored `build/` subdirectory. There is no second manuscript snapshot.

`docs/research/` preserves research notes, meeting material and historical
audit evidence. `docs/references/` contains Hevia's undated GTPPLOT article.
`relocated_paths.json` records the research-document moves. Legacy build
outputs are preserved locally under ignored `docs/archive/previous-build/`.
Historical audit manifests retain their original content digests; moved
audit-file paths are updated, while historical code digests remain dated
provenance rather than a claim about the current code revision.

## Compile

```sh
just build
```

Output: `doc/build/main.pdf`. No Python, ATP inputs, `results/` directory or
other repository files are required to compile a copy of `doc/`.

Install `just` with your package manager first. On Debian/Ubuntu:

```sh
sudo apt-get update
sudo apt-get install just
just install-deps
```

The `install-deps` recipe declares the TeX dependencies and installs them
using sudo. To build or clean from inside `doc/`:

```sh
just build
just clean
```

Running `just` without a recipe also builds the document. The `clean` recipe
preserves `doc/build/main.pdf`. Recipes use `doc/` as their working
directory. A standalone copy of `doc/` can be compiled directly with
`latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error main.tex`.

## Refresh generated evidence

From the repository root:

```sh
uv sync --locked
uv run python -m scripts.build_defense_evidence --output results/defense-evidence/v2
uv run python -m scripts.prepare_defense_document
just build
```

The generator rejects nonempty output; add `--overwrite` only to explicitly
replace a generated v2. The v1 package is preserved. The preparation script
copies only tables and figures actually referenced by `doc/main.tex` into
`doc/evidence/v2/`. The complete traceable package remains under the ignored
`results/defense-evidence/v2/` directory. Regeneration requires project data
and Python dependencies; document compilation uses the copied inputs only.
