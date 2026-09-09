# Interpretar eletricamente os resultados

## Situação

**Pendente.**

## O que deve ser feito

Relacionar os resultados estatísticos à topologia e ao comportamento transitório
do sistema. A discussão deve explicar por que determinados terminais, fases ou
configurações apresentam maiores tensões, considerando propagação e reflexão de
ondas, condição do terminal receptor, resistor de pré-inserção, equivalente de
rede e instantes de fechamento.

Cada caso classificado como relevante deve ser rastreado até a simulação e,
quando necessário, até sua forma de onda. A discussão precisa separar três
afirmações:

1. o valor é raro dentro da amostra;
2. o valor é fisicamente severo;
3. o valor é provavelmente causado por instabilidade numérica.

Essas afirmações não são equivalentes.

## Como validar

- Conferência com especialista e literatura de transitórios.
- Comparação entre terminais e fases esperada pelo modelo elétrico.
- Reexecução dos casos críticos com parâmetros numéricos alternativos.
- Rastreabilidade das interpretações até os arquivos e configurações de origem.

## Critério de conclusão

O capítulo de resultados deve responder diretamente à questão de pesquisa,
declarando até onde os métodos diferenciam eventos físicos e numéricos e quais
incertezas permanecem.

