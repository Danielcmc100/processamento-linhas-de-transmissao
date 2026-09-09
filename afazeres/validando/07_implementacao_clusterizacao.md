# Implementação do DBSCAN e do K-Means

## Status

**Validando.** Clustering implemented; feature and parameter choices remain unvalidated.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Justify the one-dimensional feature, scaling, DBSCAN parameters, K-Means cluster count, and grouping by terminal and phase.
- [ ] Evaluate sensitivity and stability across the declared cases and sample sizes, including the current zero-noise DBSCAN outcome.
- [ ] Document the analytical role and limitations of each algorithm in the methodology and results.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Analisar todas as fases e os cenários relevantes](../pendente/02_fases_e_cenarios.md)
- [Comparar formalmente os métodos](../pendente/05_comparacao_formal_metodos.md)

## Como foi feito

O DBSCAN é aplicado separadamente por terminal sobre o valor máximo em P.U. e
usa o rótulo `-1` para indicar ruído. O K-Means padroniza os valores, usa
semente fixa e ordena os rótulos pelos centróides, tornando o resultado
determinístico e interpretável.

Ambos operam sobre uma única característica, `value_pu`. Portanto, identificam
grupos de magnitudes máximas, e não padrões completos de forma de onda.

## Avaliação de validade

As rotinas possuem validação de parâmetros, tratamento de entradas vazias e
testes de regressão. Entretanto, os arquivos de configuração atuais usam
`eps = 3.0`; como os dados estão em P.U. e têm dispersão muito menor, o DBSCAN
não marcou nenhum ruído nos cinco pacotes consolidados. O K-Means é executado
globalmente, embora terminais tenham distribuições distintas.

Assim, a implementação está concluída, mas os parâmetros e o desenho analítico
não estão cientificamente justificados.

## Evidências e validação realizada

- Implementação: `src/services/clustering.py`.
- Testes: `tests/test_clustering.py`.
- Saída: `dbscan_cluster` e `kmeans_cluster` nos CSVs anotados.

## Pendência associada

A escolha dos atributos, o ajuste dos hiperparâmetros e a estabilidade dos
agrupamentos fazem parte do protocolo experimental pendente.

