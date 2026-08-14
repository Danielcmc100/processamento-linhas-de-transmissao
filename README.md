# Processamento de Dados em Linhas de Transmissão

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
