# Como calcular a probabilidade de ocorrência de um caso estatístico no ATP

## 1. Objetivo

Este guia mostra como usar os resultados de um estudo estatístico do **ATP (Alternative Transients Program)** para estimar a probabilidade de ocorrência de um determinado resultado, com base no artigo **“Gráficos Estadísticos con el GTPPLOT”**, de Orlando P. Hevia Gorostiaga.

O princípio central é simples:

> O ATP executa várias energizações/casos, variando estatisticamente os tempos de fechamento ou abertura dos disjuntores. Para cada execução, registra-se o pico da variável de interesse. A probabilidade é então obtida contando quantas execuções produziram resultados dentro de determinada faixa ou acima de determinado valor.

---

## 2. Como funciona um caso estatístico no ATP

Em um estudo estatístico, o ATP executa automaticamente uma série de simulações nas quais um ou mais tempos de abertura/fechamento de disjuntores são variados.

O artigo informa que o usuário deve definir, entre outros parâmetros:

- se o estudo será **estatístico** ou **sistemático**;
- se os tempos de operação dos disjuntores seguem uma distribuição **normal** ou **uniforme**;
- o número de operações/energizações;
- se os disjuntores são independentes ou relacionados em grupos;
- quais variáveis terão seus picos tabulados.

O número de execuções é representado no artigo por **NENERG**, enquanto internamente o ATP utiliza **KNT**.

Assim, se:

```text
NENERG = 1000
```

o ATP terá uma amostra de:

```text
KNT = 1000 resultados
```

para cada variável estatística solicitada.

---

## 3. O que o ATP registra em cada execução

Para cada energização, o ATP considera o **pico** da variável analisada.

Exemplos:

- máxima sobretensão em uma barra;
- máxima corrente em um ramo;
- máxima tensão entre dois nós;
- máxima potência;
- máxima energia.

Se várias variáveis forem agrupadas, o ATP utiliza, para cada execução, o **maior pico dentro do grupo**.

Portanto, para `KNT = 1000`, uma tabulação estatística é construída a partir de 1000 valores de pico.

---

## 4. Tabela estatística produzida pelo ATP

Uma tabela típica possui colunas semelhantes a:

```text
Interval
number

voltage
in per unit

voltage in
physical units

Frequency
(density)

Cumulative
frequency

Per cent
.GE. current value
```

As três colunas mais importantes para calcular probabilidades são:

### 4.1. Frequency (density)

É o número de resultados que caíram dentro de determinado intervalo.

Segundo o artigo, o valor de uma linha corresponde ao número de picos compreendidos entre o valor indicado naquela linha e o valor da linha anterior.

Exemplo:

```text
Intervalo: 1,40 < X <= 1,45 pu
Frequency = 2
```

significa que, entre todas as energizações, **2 casos apresentaram pico nessa faixa**.

---

### 4.2. Cumulative frequency

É a soma acumulada das frequências até aquela linha.

Seu valor varia entre:

```text
0 e KNT
```

onde `KNT` é o número total de energizações.

---

### 4.3. Per cent .GE. current value

Essa coluna indica a porcentagem de resultados **maiores ou iguais ao valor da linha**.

Ela representa diretamente uma estimativa da probabilidade de excedência:

\[
P(X \ge x)
\]

Essa é uma das formas mais úteis de avaliar a probabilidade de um cenário no ATP.

---

# 5. Probabilidade de um resultado cair em uma faixa

Se o objetivo é determinar a probabilidade de o resultado ficar em uma determinada faixa:

\[
x_1 < X \le x_2
\]

utiliza-se a frequência daquela faixa.

A estimativa é:

\[
P(x_1 < X \le x_2)
=
\frac{n_{\text{faixa}}}{KNT}
\]

onde:

- \(n_{\text{faixa}}\) = quantidade de casos naquela faixa;
- \(KNT\) = quantidade total de energizações.

### Exemplo

Suponha:

```text
KNT = 1000
```

e que:

```text
40 casos apresentaram sobretensão entre 1,90 e 1,95 pu
```

Então:

\[
P(1,90 < X \le 1,95)
=
\frac{40}{1000}
=
0,04
\]

ou:

\[
P = 4\%
\]

Portanto, aproximadamente **4% das energizações produziram resultados nessa faixa**.

---

# 6. Probabilidade de exceder determinado valor

Em muitos estudos de transitórios, a pergunta mais importante não é:

> Qual a probabilidade de ocorrer exatamente este valor?

mas sim:

> Qual a probabilidade de a sobretensão ultrapassar este valor?

Nesse caso deseja-se:

\[
P(X \ge x)
\]

O ATP já fornece essa informação na coluna:

```text
Per cent .GE. current value
```

---

## Exemplo

No exemplo apresentado no artigo, uma tabela com `KNT = 1000` contém:

```text
Valor       Cumulative frequency       Per cent .GE.
1,10 pu                1                  99,9 %
...
2,80 pu              999                   0,1 %
2,85 pu             1000                   0,0 %
```

Isso significa, por exemplo, que aproximadamente:

\[
P(X \ge 2,80) = 0,1\%
\]

ou, em forma decimal:

\[
P(X \ge 2,80) = 0,001
\]

Em 1000 energizações, isso corresponde aproximadamente a **1 caso**.

---

# 7. Calculando manualmente a probabilidade de excedência

Se você possuir apenas as frequências acumuladas, a probabilidade também pode ser calculada manualmente.

Se:

- \(KNT\) = número total de casos;
- \(F_{\text{acum}}(x)\) = número de resultados abaixo do limite associado à linha;

então a probabilidade de excedência pode ser estimada por:

\[
P(X \ge x)
\approx
1 -
\frac{F_{\text{acum}}(x)}{KNT}
\]

A definição exata da borda do intervalo depende do encasillamento utilizado pelo ATP, portanto, para evitar erro de interpretação, é preferível usar diretamente a coluna:

```text
Per cent .GE. current value
```

quando ela estiver disponível.

---

# 8. Probabilidade de um cenário definido por limite

Suponha que o critério do estudo seja:

```text
Sobretensão máxima >= 2,0 pu
```

O cenário de interesse é então:

\[
X \ge 2,0
\]

Se, em 1000 energizações, 137 atingiram ou ultrapassaram 2,0 pu:

\[
P(X \ge 2,0)
=
\frac{137}{1000}
\]

\[
P = 0,137
\]

\[
P = 13,7\%
\]

Assim, pode-se escrever:

> Para as condições estatísticas utilizadas no ATP, aproximadamente 13,7% das energizações produziram sobretensão máxima igual ou superior a 2,0 pu.

É importante dizer **“para as condições estatísticas utilizadas”**, pois a probabilidade depende diretamente das distribuições e parâmetros utilizados para os tempos de operação dos disjuntores.

---

# 9. Probabilidade de um cenário definido por intervalo

Também é possível definir um cenário como:

```text
2,0 pu <= X < 2,2 pu
```

Se:

```text
Quantidade total de casos = 1000
Casos entre 2,0 e 2,2 pu = 92
```

então:

\[
P(2,0 \le X < 2,2)
=
\frac{92}{1000}
=
9,2\%
\]

Outra possibilidade é usar duas probabilidades de excedência:

\[
P(2,0 \le X < 2,2)
=
P(X \ge 2,0)
-
P(X \ge 2,2)
\]

Por exemplo:

\[
P(X \ge 2,0)=13,7\%
\]

e:

\[
P(X \ge 2,2)=4,5\%
\]

logo:

\[
P(2,0 \le X < 2,2)
=
13,7 - 4,5
=
9,2\%
\]

---

# 10. Média, variância e desvio padrão fornecidos pelo ATP

Depois da tabulação, o ATP apresenta um resumo com:

- média;
- variância;
- desvio padrão;
- valores para dados agrupados;
- valores para dados não agrupados.

O artigo indica:

\[
\bar X =
\frac{1}{KNT}
\sum_{j=1}^{KNT} X_j
\]

A variância amostral é calculada dividindo-se por:

\[
KNT-1
\]

e o desvio padrão é:

\[
\sigma = \sqrt{s^2}
\]

No exemplo apresentado:

```text
Ungrouped data

Mean               = 1.78070337 pu
Variance           = 1.02060609E-01
Standard deviation = 3.19469262E-01 pu
```

Essas grandezas ajudam a caracterizar estatisticamente os resultados, mas a tabela de frequências continua sendo a forma direta de calcular a probabilidade empírica observada nas simulações.

---

# 11. Valor com 2% de probabilidade de ser excedido

O GTPPLOT também calcula um valor chamado no artigo de:

```text
2% overvoltage
```

A expressão utilizada é:

\[
X_{2\%}
=
\bar X
+
2,0537494\,\sigma
\]

Esse valor representa um nível de sobretensão associado a uma **probabilidade de excedência de 2%** dentro da aproximação estatística utilizada pelo programa.

No exemplo do artigo:

```text
Ungrouped data

Mean               = 1.78070337 pu
Standard deviation = 0.319469262 pu
```

Então:

\[
X_{2\%}
=
1,78070337
+
2,0537494(0,319469262)
\]

resultando aproximadamente em:

\[
X_{2\%}
=
2,43824\ pu
\]

que coincide com o resultado mostrado pelo GTPPLOT:

```text
2% overvoltage = 2.43824269 pu
```

Isso pode ser interpretado como:

\[
P(X \ge 2,43824\ pu)
\approx
2\%
\]

dentro da aproximação utilizada.

---

# 12. Curva de probabilidade de excedência

Quando `NSTATI` é diferente de zero, o GTPPLOT pode gerar, além do histograma, um gráfico de:

\[
P(X \ge x)
\]

em função de \(x\).

Segundo o artigo:

```text
NSTATI = 0
```

mostra apenas os compartimentos do histograma.

```text
NSTATI = 1
```

utiliza a variável em **por unidade**.

```text
NSTATI = 2
```

utiliza valores em unidades físicas, como:

- V;
- A;
- W;
- J.

O artigo também mostra duas formas de representar a curva:

- pontos unidos por segmentos;
- gráfico em **escada**.

O próprio autor observa que a forma em escada pode ser mais coerente, pois os dados do ATP estão agrupados em compartimentos.

---

# 13. Configurando os compartimentos da distribuição

O parâmetro:

```text
AINCR
```

controla o tamanho dos intervalos utilizados na tabela.

Por exemplo:

```text
STATISTICS DATA 3 0.05 2.0
```

utiliza:

```text
AINCR = 0.05 pu
```

Assim, os resultados podem ser agrupados em intervalos semelhantes a:

```text
1.00 – 1.05
1.05 – 1.10
1.10 – 1.15
...
```

Quanto menor o `AINCR`, maior a resolução do histograma, desde que haja número suficiente de energizações.

Também é possível utilizar `AINCR` negativo para solicitar um número fixo de compartimentos.

---

# 14. Procedimento recomendado no ATP

## Etapa 1 — Definir o experimento estatístico

Defina:

```text
Número de energizações
Distribuição dos tempos de fechamento
Média dos tempos
Desvio padrão, quando aplicável
Independência ou agrupamento dos disjuntores
```

Essas definições determinam o espaço probabilístico que está sendo simulado.

---

## Etapa 2 — Escolher a variável de interesse

Exemplo:

```text
Tensão máxima na barra FASEA2
```

ou:

```text
Máxima sobretensão entre todas as fases
```

---

## Etapa 3 — Solicitar a tabulação estatística

Um exemplo apresentado no artigo é:

```text
STATISTICS DATA 3 0.05 2.0
```

onde:

```text
MODTAB = 3
AINCR  = 0.05 pu
XMAXMX = 2.0 pu
```

`MODTAB = 3` solicita tanto tabelas individuais quanto a tabela agrupada `SUMMARY`.

---

## Etapa 4 — Executar muitas energizações

Por exemplo:

```text
NENERG = 1000
```

O ATP executará 1000 combinações estatísticas dos instantes de operação definidos.

---

## Etapa 5 — Ler a tabela no arquivo `.lis`

Procure uma seção semelhante a:

```text
Statistical distribution of peak voltage
```

e identifique as colunas:

```text
Frequency (density)
Cumulative frequency
Per cent .GE. current value
```

---

## Etapa 6 — Definir matematicamente o cenário

Exemplos:

### Caso A

```text
Sobretensão >= 2,0 pu
```

\[
A=\{X\ge2,0\}
\]

### Caso B

```text
Sobretensão entre 1,8 e 2,0 pu
```

\[
B=\{1,8\le X<2,0\}
\]

### Caso C

```text
Sobretensão >= 2,5 pu
```

\[
C=\{X\ge2,5\}
\]

---

## Etapa 7 — Calcular a probabilidade

### Pela contagem direta

\[
P(A)
=
\frac{N_A}{N_{\text{total}}}
\]

onde:

```text
N_A = número de energizações que satisfazem o cenário
N_total = KNT = NENERG
```

### Pela coluna de excedência

Para cenários da forma:

\[
X\ge x
\]

basta utilizar:

```text
Per cent .GE. current value
```

---

# 15. Exemplo completo

Considere:

```text
NENERG = 1000
```

e suponha que o ATP produza:

| Sobretensão | Frequency | Probabilidade de excedência |
|---:|---:|---:|
| 1,80 pu | 55 | 42,0% |
| 1,85 pu | 61 | 36,5% |
| 1,90 pu | 58 | 30,4% |
| 1,95 pu | 47 | 24,6% |
| 2,00 pu | 41 | 19,9% |
| 2,05 pu | 36 | 15,8% |
| 2,10 pu | 30 | 12,2% |

Se o cenário analisado for:

```text
X >= 2,00 pu
```

então:

\[
P(X\ge2,00)
=
19,9\%
\]

Se o cenário for:

```text
2,00 <= X < 2,10
```

então:

\[
P(2,00\le X<2,10)
=
P(X\ge2,00)-P(X\ge2,10)
\]

\[
=
19,9-12,2
\]

\[
=
7,7\%
\]

---

# 16. Diferença entre probabilidade dos tempos de chaveamento e probabilidade do resultado

É importante separar dois conceitos.

## Entrada estatística

A distribuição escolhida para os tempos de operação dos disjuntores determina **como os casos são sorteados**.

Por exemplo:

\[
T\sim N(\mu,\sigma^2)
\]

significa que o instante de fechamento está sendo amostrado a partir de uma distribuição normal.

## Resultado estatístico

Depois de cada sorteio, o ATP resolve o transitório e obtém uma grandeza:

\[
T
\longrightarrow
X_{\text{pico}}
\]

Após muitas simulações:

\[
T_1,T_2,\ldots,T_{KNT}
\]

produzem:

\[
X_1,X_2,\ldots,X_{KNT}
\]

A distribuição de \(X\) não precisa necessariamente ter a mesma forma da distribuição usada para sortear os tempos de chaveamento.

Por isso, para calcular a probabilidade de **um resultado elétrico** ocorrer, deve-se utilizar a distribuição empírica dos resultados produzida pelo ATP.

---

# 17. Fórmula geral para usar no trabalho

Para qualquer cenário \(A\) definido sobre os resultados das simulações:

\[
\boxed{
P(A)
\approx
\frac{N(A)}{NENERG}
}
\]

onde:

- \(N(A)\) é o número de execuções nas quais o cenário ocorreu;
- `NENERG` é o número total de energizações.

Por exemplo:

\[
\boxed{
P(V_{\max}\ge V_{\text{limite}})
\approx
\frac{N(V_{\max}\ge V_{\text{limite}})}
{NENERG}
}
\]

Para um cenário de excedência, essa estimativa é justamente a informação apresentada pela coluna:

```text
Per cent .GE. current value
```

das tabelas estatísticas do ATP.

---

# 18. Interpretação recomendada

Evite escrever:

> Existe 10% de chance de essa sobretensão acontecer em qualquer situação.

Prefira:

> Considerando as distribuições estatísticas e os parâmetros de chaveamento adotados no estudo, 10% das energizações simuladas produziram uma sobretensão igual ou superior ao limite analisado.

A probabilidade obtida é condicionada ao modelo utilizado:

\[
P(\text{resultado}\mid\text{modelo estatístico adotado})
\]

Portanto, alterações em:

- média dos tempos de fechamento;
- dispersão dos tempos;
- distribuição normal ou uniforme;
- correlação entre polos/disjuntores;
- topologia da rede;
- instante de energização;
- número de energizações;

podem alterar a distribuição observada dos resultados.

---

# 19. Resumo do método

```text
1. Definir a distribuição estatística dos tempos de operação.
                          ↓
2. Executar NENERG casos no ATP.
                          ↓
3. Obter o pico da variável em cada execução.
                          ↓
4. Solicitar a tabulação estatística.
                          ↓
5. Obter Frequency e Cumulative frequency.
                          ↓
6. Definir o cenário de interesse.
                          ↓
7. Contar quantos casos satisfazem o cenário.
                          ↓
8. Dividir pelo número total de energizações.
```

Matematicamente:

\[
\boxed{
P(\text{cenário})
\approx
\frac{\text{número de ocorrências}}
{\text{número total de energizações}}
}
\]

Para limites de excedência:

\[
\boxed{
P(X\ge x)
}
\]

pode ser obtido diretamente na coluna:

```text
Per cent .GE. current value
```

---

# 20. Referência utilizada

HEVIA GOROSTIAGA, Orlando P. **Gráficos Estadísticos con el GTPPLOT**. CAUE — Comité Argentino de Usuarios del EMTP, Santa Fe, Argentina.

Pontos principais utilizados deste artigo:

- funcionamento dos estudos estatísticos do ATP;
- uso de `NENERG/KNT`;
- tabelas de frequência e frequência acumulada;
- coluna de probabilidade de excedência;
- parâmetros `MODTAB`, `AINCR` e `XMAXMX`;
- gráficos estatísticos do GTPPLOT;
- cálculo de \(X_{2\%}\);
- exemplo com 1000 energizações.
