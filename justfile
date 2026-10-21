set working-directory := "doc"

# Compile the standalone thesis into build/main.pdf.
build:
    latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error main.tex

# Remove auxiliary files while preserving the PDF.
clean:
    latexmk -outdir=build -c main.tex

# Install thesis build dependencies on Debian or Ubuntu.
install-deps:
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends latexmk texlive-latex-extra texlive-fonts-recommended texlive-lang-portuguese texlive-science texlive-pictures texlive-publishers texlive-font-utils ghostscript
