# Validação e limpeza dos dados

## Status

**Validando.** Structural validation implemented; experimental integrity still needs validation.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Define and verify source-run-terminal-phase uniqueness, declared versus extracted counts, and completeness for the experimental matrix.
- [ ] Document admissible time ranges and the rationale for exclusions, with retained records of excluded observations.
- [ ] Validate the rules against deliberately corrupted and independently checked cases; report their effect on the analyzed sample.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Analisar todas as fases e os cenários relevantes](../pendente/02_fases_e_cenarios.md)

## Como foi feito

O serviço `validate_observations` verifica o esquema, os tipos das colunas, os
campos de identificação e a presença de valores finitos para tensão e tempo.
Também confirma se os terminais e as fases solicitados existem. Linhas com
valores não finitos são registradas como problemas e removidas; inconsistências
de identidade ou esquema impedem a análise.

O resultado preserva um estado explícito, uma lista de problemas encontrados e
a tabela limpa usada pelo pipeline.

## Avaliação de validade

A rotina é válida para impedir que entradas estruturalmente inválidas cheguem
aos modelos estatísticos. Ela não constitui uma validação física completa. Não
verifica duplicidades, correspondência entre `NENERG` e o total extraído,
completude por terminal e fase, limites físicos de tensão ou coerência temporal.

## Evidências e validação realizada

- Implementação: `src/services/validation.py`.
- Integração obrigatória: `src/services/pipeline.py`.
- Testes de estados válidos e inválidos: `tests/test_validation.py`.

## Próxima melhoria recomendada

Adicionar regras de integridade experimental, como unicidade da chave
arquivo–simulação–terminal–fase, quantidade esperada de observações e intervalo
admissível dos tempos. Essas regras devem ter testes com dados deliberadamente
corrompidos.

