# Ajuste Gaussiano e probabilidades de excedência

## Status

**Validando.** Gaussian fitting implemented; distribution adequacy has not been demonstrated.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Complete the Gaussian assessment for each group in the protocol and record an explicit decision about model adequacy and tail limitations.
- [ ] Compare empirical and fitted exceedance with documented uncertainty and account for filtering and sample selection.
- [ ] Document the supported probability estimator, including an alternative where needed, and link diagnostics and results in the thesis.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Validar a hipótese Gaussiana](../pendente/03_validacao_hipotese_gaussiana.md)

## Como foi feito

O método ajusta uma distribuição Normal usando a média e o desvio padrão
amostral dos eventos considerados válidos. Para um limite de tensão configurado,
calcula:

- a frequência empírica, pela proporção de observações acima do limite;
- a probabilidade Gaussiana, pela função de sobrevivência da Normal ajustada.

Também são geradas curvas de excedência e níveis de um a seis sigmas.

## Avaliação de validade

As fórmulas e a implementação com SciPy são válidas sob o modelo Normal. A
probabilidade Gaussiana não deve ser tratada como estimativa comprovada enquanto
não forem examinados ajuste, assimetria, caudas e possíveis misturas entre
cenários. A frequência empírica é diretamente observável, mas também necessita
de intervalo de confiança para expressar sua incerteza.

## Evidências e validação realizada

- Implementação: `src/services/statistics.py`.
- Visualização: `src/services/visualization.py`.
- Testes: `tests/test_statistics.py` e `tests/test_visualization.py`.
- Saída: `empirical_exceedance` e `gaussian_exceedance` em `summary.csv`.

## Limite da conclusão atual

Pode-se afirmar que as probabilidades foram calculadas. Ainda não se pode
afirmar que a distribuição Gaussiana descreve adequadamente todos os conjuntos
analisados.

