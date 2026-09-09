# Validar tecnicamente as anomalias

## Situação

**Pendente e essencial para responder ao problema de pesquisa.**

## Estado atual

O software gera candidatas a anomalia, mas não comprova se elas são fenômenos
físicos ou erros numéricos. O DBSCAN não marcou ruídos nos resultados atuais, e
o grupo superior do K-Means faz com que aproximadamente metade dos pontos seja
marcada como candidata.

## O que deve ser feito

Construir uma referência de validação por uma ou mais estratégias:

- revisão dos casos por especialista em transitórios;
- reinspeção da forma de onda e do arquivo ATP da simulação indicada;
- repetição com passo de integração menor ou configuração numérica alternativa;
- injeção controlada de erros conhecidos em uma base de teste;
- regras físicas documentadas para coerência entre fases, terminais e tempos.

Uma tensão alta não deve ser rotulada automaticamente como erro. A classe final
pode separar, por exemplo, evento físico extremo, suspeita numérica, dado
inválido e caso inconclusivo.

## Como validar

Comparar as previsões com a referência e calcular matriz de confusão, precisão,
revocação e falsos positivos quando houver rótulos suficientes. Em revisões de
especialistas, medir concordância e registrar justificativas.

## Critério de conclusão

O trabalho deverá apresentar evidência externa aos próprios algoritmos que
sustente a interpretação de pelo menos um conjunto representativo de casos.

