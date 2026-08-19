# Processamento de Dados em Linhas de Transmissão

## Running the analysis

### Install the project

The project requires Python 3.13 or newer and
[`uv`](https://docs.astral.sh/uv/). Install the locked dependencies from the
repository root:

```bash
uv sync
```

### Create the analysis configuration

Create an `analysis-config.json` file. The input directory must already exist;
the output directory is created automatically when necessary.

```json
{
  "input_path": "tests/fixtures",
  "encoding": "iso-8859-1",
  "base_voltage": 100000.0,
  "terminals": ["T_MAN", "T_OPO"],
  "phase_policy": "A",
  "dbscan": {
    "eps": 3.0,
    "min_samples": 2
  },
  "kmeans": {
    "n_clusters": 2,
    "random_state": 42
  },
  "threshold": 2.3,
  "output_dir": "results/representative-a",
  "overwrite": false
}
```

The main parameters are:

- `input_path`: directory searched recursively for ATP `.lis` files.
- `base_voltage`: voltage base in volts used for P.U. normalization.
- `terminals`: terminal names without the phase suffix (`A`, `B`, or `C`).
- `phase_policy`: the single phase analyzed in this run.
- `dbscan`: DBSCAN neighborhood and minimum-sample parameters.
- `kmeans`: number of clusters and deterministic random seed. The number of
  clusters cannot exceed the selected observation count.
- `threshold`: P.U. value used for empirical and Gaussian exceedance results.
- `output_dir`: directory that receives the result package.
- `overwrite`: when `false`, the run stops before replacing an existing result
  artifact; when `true`, only known result artifacts are replaced.

### Execute the pipeline

Run the command from the repository root:

```bash
uv run python main.py analysis-config.json
```

Each successful run writes the following files to `output_dir`:

- `raw_observations.csv`
- `annotated_observations.csv`
- `summary.csv`
- `configuration.json`
- `metadata.json`
- `combined.png`
- `exceedance.png`

The saved `configuration.json` can be passed to the same command to reproduce
the analysis. Select a new output directory or set `overwrite` to `true` when
regenerating an existing package.

## Compilação do TCC

O documento principal está em [`doc/main.tex`](doc/main.tex). A compilação deve
ser executada a partir da pasta `doc`, pois o arquivo utiliza caminhos relativos
para as imagens, referências bibliográficas e o estilo LaTeX.

### Dependências

Em sistemas Ubuntu ou Debian, instale o LaTeX e os pacotes necessários com:

```bash
sudo apt update
sudo apt install latexmk texlive-latex-extra \
    texlive-publishers texlive-lang-portuguese \
    texlive-fonts-recommended texlive-science
```

### Compilação automática

```bash
cd doc
latexmk -pdf -interaction=nonstopmode -file-line-error main.tex
```

O arquivo `doc/main.pdf` será gerado após a compilação. O `latexmk` executa
automaticamente as passagens necessárias do LaTeX, incluindo o processamento
da bibliografia com BibTeX e a atualização do índice.

### Compilação manual

Caso o `latexmk` não esteja disponível, execute:

```bash
cd doc
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Limpeza dos arquivos auxiliares

Para remover arquivos temporários gerados pela compilação, mantendo o PDF:

```bash
cd doc
latexmk -c
```
