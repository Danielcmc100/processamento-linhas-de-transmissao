# Artefatos e reprodutibilidade das execuções

## Status

**Validando.** Artifact generation implemented; reproduction of thesis results remains to be demonstrated.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Record the code revision, environment, source hashes, and justified configurations for the final experimental scope.
- [ ] Rerun a documented selection of cases and compare numerical artifacts using declared tolerances, accounting for variable metadata such as timestamps.
- [ ] Link thesis tables and figures to their generating artifacts and record the reproduction outcome.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Analisar todas as fases e os cenários relevantes](../pendente/02_fases_e_cenarios.md)
- [Redigir os capítulos finais](../pendente/07_capitulos_finais.md)

## Como foi feito

Cada execução recebe uma configuração validada contendo entrada, codificação,
base de tensão, terminais, fase, hiperparâmetros, limite de excedência e pasta
de saída. O pipeline grava observações brutas e anotadas, resumo estatístico,
configuração, metadados e quatro gráficos.

Os metadados registram versões do software, quantidades processadas e o hash
SHA-256 de cada arquivo `.lis`. Arquivos existentes não são sobrescritos sem
autorização explícita, e arquivos alheios ao pacote não são removidos.

## Avaliação de validade

A solução permite identificar quais entradas, parâmetros e versões produziram
cada pacote. Isso fornece boa rastreabilidade computacional. A reprodução
científica ainda depende de documentar por que cada cenário e parâmetro foi
escolhido, algo que não é resolvido apenas pelos metadados.

## Evidências e validação realizada

- Configuração: `src/services/config.py`.
- Orquestração: `src/services/pipeline.py` e `main.py`.
- Escrita e proveniência: `src/services/reporting.py`.
- Testes: `tests/test_config.py`, `tests/test_pipeline.py` e
  `tests/test_reporting.py`.
- Instruções de execução: `README.md`.

## Critério atendido

Uma execução pode ser repetida com a configuração salva, desde que os arquivos
de entrada identificados pelos hashes estejam disponíveis.

