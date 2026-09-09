# Execuções por tamanho de amostra

## Status

**Validando.** Reference sample-size runs exist; convergence and experimental coverage remain open.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Document how each sample set was generated, including seeds, repetitions, and any overlap or dependence between sets.
- [ ] Compare estimates and uncertainty across the five sample sizes and state the supported convergence conclusion.
- [ ] Complete the selected phase/scenario matrix or justify exclusions, and integrate the comparison into the results chapter.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Analisar todas as fases e os cenários relevantes](../pendente/02_fases_e_cenarios.md)
- [Comparar formalmente os métodos](../pendente/05_comparacao_formal_metodos.md)

## Como foi feito

Existem pacotes de resultados para 50, 100, 200, 1.000 e 10.000 simulações.
Cada pacote contém CSVs, gráficos, configuração e metadados. The annotated tables contain 150, 300, 600, 3,000, and 30,000
observations, respectively, for three terminals of phase A. Metadata records
450, 900, 1,800, 9,000, and 90,000 raw observations before phase selection.

Essa série permite observar como médias, dispersões e probabilidades estimadas
mudam com o tamanho da amostra.

## Avaliação de validade

Os arquivos demonstram que o pipeline processa diferentes volumes e produz
saídas consistentes. Porém, todos os `input.json` consolidados selecionam a fase
A e o caminho `T_MAN/SRPI/CASO-COMPLETO/SDEF`. Portanto, eles não representam o
conjunto completo de fases e configurações disponíveis.

Também falta uma análise formal da convergência das estimativas entre os cinco
tamanhos. A simples existência dos pacotes não substitui essa comparação.

## Evidências e validação realizada

- Entradas e resultados: `input_files/casos/*-simulacoes/`.
- Os resumos apresentam três linhas válidas, uma por terminal, em cada pacote.
- Os metadados permitem conferir contagens e hashes dos arquivos processados.

## Uso correto neste estágio

Os pacotes podem ser usados como estudo preliminar de tamanho amostral, mas não
como experimento final de todos os cenários.

