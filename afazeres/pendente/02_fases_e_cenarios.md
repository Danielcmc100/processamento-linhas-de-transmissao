# Analisar todas as fases e os cenários relevantes

## Situação

**Pendente.**

## Estado atual

Os pacotes consolidados analisam somente a fase A de um cenário localizado em
`T_MAN/SRPI/CASO-COMPLETO/SDEF`. A base contém outras fases e combinações, como
casos com e sem resistor de pré-inserção, diferentes equivalentes e diferentes
condições de defeito.

## O que deve ser feito

Executar a matriz definida no protocolo para as fases A, B e C e para os
cenários eletricamente relevantes. Cada execução deve ter pasta própria,
configuração salva e metadados. Em seguida, construir uma tabela consolidada
que compare terminais, fases, cenários e tamanhos de amostra.

Também deve ser decidido se o pipeline continuará aceitando uma fase por
execução ou se será ampliado para processar as três fases em uma única chamada.
Ambas as opções são válidas se a organização for reproduzível.

## Como validar

- Conferir o número esperado de observações por arquivo, fase e terminal.
- Comparar amostras do CSV com os máximos presentes no `.lis`.
- Verificar se todas as células previstas na matriz experimental possuem
  resultado ou justificativa para ausência.
- Reexecutar uma amostra de configurações e comparar os artefatos numéricos.

## Critério de conclusão

Todas as fases e todos os cenários definidos no escopo final devem estar
processados, conferidos e resumidos em uma tabela-mestra.

## CRPI validation prerequisite — 2026-09-10

The [CRPI findings](../../doc/crpi_validation_findings.md) identify shifted
headers, duplicate terminal/phase observations, and absent `T_OPO` values in
all five examined CRPI sizes. Before consolidating CRPI results, complete
[TCCKL-8](../concluido/01_parser_arquivos_atp.md) header correction and
[TCCKL-9](../validando/02_estruturacao_observacoes.md) source mapping,
completeness, and uniqueness validation. Correct total row counts alone are
insufficient. This task remains pending; the previous SRPI acceptance does
not extend to CRPI.
