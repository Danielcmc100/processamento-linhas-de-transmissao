# Comparar formalmente os métodos

## Situação

**Pendente.** A tabela conjunta existe, mas ainda não há avaliação comparativa
conclusiva.

## O que deve ser feito

Comparar regra de três sigmas, DBSCAN e K-Means por cenário, fase e terminal.
A análise deve mostrar:

- quantidade e proporção de candidatos por método;
- interseções e divergências entre os métodos;
- estabilidade diante de mudanças de amostra e hiperparâmetros;
- desempenho contra a referência técnica, quando disponível;
- custo interpretativo e limitações de cada abordagem.

É necessário revisar a regra atual que considera todo o grupo de maior
centróide do K-Means como indício. O K-Means é um método de agrupamento, não um
detector de anomalia por definição. Uma pontuação por distância ao centróide,
tamanho do grupo ou combinação com critérios físicos pode ser mais defensável,
desde que validada.

## Como validar

Usar tabelas de contingência, métricas contra rótulos de referência e análise de
sensibilidade. Caso não exista verdade de referência suficiente, limitar a
conclusão a concordância exploratória, sem declarar qual método identifica
erros corretamente.

## Critério de conclusão

A comparação deve indicar claramente o que cada método detecta, quando produz
falsos alertas e qual papel terá na rotina final.

