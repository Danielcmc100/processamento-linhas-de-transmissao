set working-directory := "doc"

# Compile the standalone thesis into build/main.pdf.
build:
    latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error main.tex

# Compile the presentation and speaker notes into build/apresentacao/.
build-presentation:
    latexmk -pdf -outdir=build/apresentacao -interaction=nonstopmode -halt-on-error apresentacao.tex roteiro_apresentacao.tex

# Pass --overwrite only when deliberately replacing the existing v10 package.
# Generate v10 evidence and compile the thesis, slides and speaker notes.
build-v10 *args:
    uv --directory .. run python -m scripts.build_defense_evidence --output results/defense-evidence/v10 {{args}}
    uv --directory .. run python -m scripts.prepare_defense_document
    latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error main.tex
    latexmk -pdf -outdir=build/apresentacao -interaction=nonstopmode -halt-on-error apresentacao.tex roteiro_apresentacao.tex

# Remove auxiliary files while preserving the PDF.
clean:
    latexmk -outdir=build -c main.tex

# Install thesis build dependencies on Debian or Ubuntu.
install-deps:
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends latexmk texlive-latex-extra texlive-fonts-recommended texlive-lang-portuguese texlive-science texlive-pictures texlive-publishers texlive-font-utils ghostscript
