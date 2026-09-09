# Comparação computacional dos indícios de anomalia

## Status

**Validando.** Candidate comparison implemented; numerical-error classification is unvalidated.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Evaluate the highest-centroid and any-signal candidate rules against a documented reference independent of the clustering outputs.
- [ ] Report method agreement and disagreements; report classification performance only where reference labels support it.
- [ ] Trace representative decisions to ATP cases and document uncertainty and physical interpretation before claiming numerical-error detection.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Validar tecnicamente as anomalias](../pendente/04_validacao_anomalias.md)
- [Comparar formalmente os métodos](../pendente/05_comparacao_formal_metodos.md)
- [Interpretar eletricamente os resultados](../pendente/06_interpretacao_eletrica.md)

## Como foi feito

A função `compare_anomaly_methods` reúne três sinais por observação:

1. tensão acima do limite de três sigmas;
2. rótulo de ruído do DBSCAN;
3. participação no grupo de maior centróide do K-Means.

O CSV registra o número de métodos concordantes, os motivos e um indicador de
“candidata a anomalia”. O próprio código declara que esses sinais não comprovam
erro numérico nem causa física.

## Avaliação de validade

A comparação é rastreável e determinística. Porém, basta um sinal para marcar
uma candidata. Como todo membro do grupo superior do K-Means conta como sinal,
aproximadamente metade das observações atuais recebe essa marca. Um grupo de
tensões mais altas pode representar uma população física legítima, não uma
anomalia.

Nos resultados consolidados, o DBSCAN marcou zero ruídos, reforçando que a
regra combinada ainda não pode fundamentar a separação entre fenômeno físico e
erro do ATP.

## Evidências e validação realizada

- Implementação: `src/services/comparison.py`.
- Testes funcionais: `tests/test_comparison.py`.
- Evidência empírica: `annotated_observations.csv` dos cinco tamanhos de amostra.

## Uso correto neste estágio

O campo deve ser descrito como triagem exploratória. A validação técnica e a
definição de uma regra final permanecem pendentes.

