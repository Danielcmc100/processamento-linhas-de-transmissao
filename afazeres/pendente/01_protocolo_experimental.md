# Definir o protocolo experimental

## Situação

**Pendente e prioritário.**

## Estado atual

O pipeline permite configurar fase, terminais, limite, DBSCAN e K-Means, mas os
valores atuais ainda não possuem justificativa experimental documentada. Em
especial, `eps = 3.0` resultou em zero ruídos do DBSCAN nos cinco pacotes
consolidados.

## O que deve ser feito

1. Definir as perguntas e hipóteses de cada experimento.
2. Delimitar cenários, fases, terminais, tamanhos de amostra e repetições.
3. Explicar a escolha do limite de 2,3 P.U.
4. Definir como selecionar `eps`, `min_samples` e o número de grupos.
5. Estabelecer previamente métricas, gráficos e regras de comparação.
6. Separar análise exploratória da avaliação final, evitando ajustar e avaliar
   o método sobre a mesma evidência sem controle.

## Como validar

Registrar o protocolo no capítulo de metodologia antes de consolidar os
resultados. Executar análise de sensibilidade dos hiperparâmetros e verificar a
estabilidade das conclusões. As escolhas devem ser justificadas por literatura,
características da escala dos dados ou critério explícito, e não apenas pelo
resultado visual desejado.

## Critérios de conclusão

- Matriz de experimentos fechada e reproduzível.
- Parâmetros e limites tecnicamente justificados.
- Métricas e critérios de decisão definidos antecipadamente.
- Configurações versionadas junto aos resultados finais.

## Validation dependencies — 2026-09-10

The [CRPI findings](../../doc/crpi_validation_findings.md) are tracked in
[TCCKL-8](../validando/01_parser_arquivos_atp.md) for header alignment repair
and [TCCKL-9](../validando/02_estruturacao_observacoes.md) for observation
completeness and uniqueness. TCCKL-20 remains pending and owns the protocol,
not these corrections. Protocol drafting can continue, but CRPI-based evidence
must wait for source-to-observation validation. No identical switching vectors
were found between sample sizes within either scenario; this does not establish
statistical independence or require new batches by itself.
