# Estatística descritiva e regra de três sigmas

## Status

**Validando.** Descriptive statistics and flags implemented; scientific interpretation remains open.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Independently reproduce sample mean, sample standard deviation, and the upper three-sigma threshold for identified groups.
- [ ] Document that the pipeline computes statistics after DBSCAN noise removal; compare results before and after this filter.
- [ ] Link the distribution assessment and state the supported meaning of a sigma flag without treating it as proof of numerical error.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Validar a hipótese Gaussiana](../pendente/03_validacao_hipotese_gaussiana.md)
- [Comparar formalmente os métodos](../pendente/05_comparacao_formal_metodos.md)

## Como foi feito

O serviço estatístico calcula, por terminal e fase, o número de amostras, a
média, o desvio padrão amostral (`ddof=1`) e o limite superior
`média + 3 × desvio padrão`. O pipeline aplica esse limite às observações e cria
o indicador booleano `sigma_flag`.

Casos com menos de duas amostras ou variância nula recebem estados específicos,
evitando resultados probabilísticos indevidos.

## Avaliação de validade

Os cálculos estão matematicamente corretos e possuem testes unitários. Contudo,
a regra de três sigmas não demonstra sozinha que um ponto é erro numérico. Sua
interpretação usual é mais defensável quando a distribuição é aproximadamente
normal, estável e sem misturas relevantes de populações.

Além disso, no pipeline atual, as estatísticas são calculadas depois da remoção
dos ruídos indicados pelo DBSCAN. Essa ordem precisa ser declarada, pois os
limites dependem do filtro anterior.

## Evidências e validação realizada

- Implementação: `src/services/statistics.py` e `src/services/pipeline.py`.
- Testes: `tests/test_statistics.py` e `tests/test_pipeline.py`.
- Saída: colunas `mean`, `std` e `sigma_3_threshold` em `summary.csv`.

## Validação científica relacionada

A adequação da hipótese normal e a sensibilidade à ordem dos filtros ainda são
pendências documentadas separadamente.

