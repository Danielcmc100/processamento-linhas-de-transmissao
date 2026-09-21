## Proposta de TCC: Processamento de Dados em Linhas de Transmissão Durante Manobras de Energização

### 1. Caracterização do Problema

O monitoramento e a análise de manobras de energização em Linhas de Transmissão (LT) são cruciais para garantir a integridade dos ativos elétricos. Devido à impossibilidade técnica e ao alto custo de realizar testes físicos reais nessas infraestruturas, a engenharia recorre a simulações computacionais extensivas via software **ATP (Alternative Transients Program)**.

O desafio reside na interpretação do volume massivo de dados sintéticos gerados. Frequentemente, os resultados apresentam **outliers** que podem ser interpretados erroneamente: ora como fenômenos físicos extremos, ora como meras instabilidades numéricas do software de simulação. A falta de uma distinção clara entre esses eventos pode levar ao sobredimensionamento do isolamento, gerando custos desnecessários, ou ao subdimensionamento, pondo em risco a rede.

### 2. Objetivos

* **Geral:** Desenvolver um modelo analítico baseado em Ciência de Dados para interpretar o desempenho de LTs sob manobras de energização, automatizando a detecção de erros e a classificação de sobretensões.
* **Específicos:**
* Implementar algoritmos de **Clusterização (Aprendizado Não Supervisionado)** para agrupar padrões de tensão nas fases A, B e C.
* Aplicar modelos estatísticos de **Distribuição Gaussiana** com fixação de desvio padrão ($3\sigma$) para validar a confiabilidade dos dados simulados.
* Identificar e filtrar erros numéricos originados no ATP, separando-os de eventos físicos de sobretensão.



### 3. Justificativa

A aplicação de técnicas de Machine Learning neste contexto permite uma **Otimização de Isolamento** baseada em evidências estatísticas. Ao determinar com precisão a probabilidade e a confiança de ocorrência de valores extremos, é possível reduzir significativamente o Capex (investimento em capital) da empresa em novos projetos de transmissão, garantindo uma margem de segurança robusta e cientificamente validada.

---

## Metodologia Sugerida

Para alinhar o projeto aos seus interesses e às necessidades da empresa, a abordagem seguirá este fluxo:

1. **Extração:** Parsing de arquivos de saída do ATP.
2. **Tratamento:** Limpeza de dados e normalização estatística.
3. **Análise:** Aplicação de algoritmos como **K-Means** ou **DBSCAN** para detecção de anomalias (outliers).
4. **Validação:** Teste de hipóteses para verificar se os extremos seguem a distribuição esperada ou se são erros de cálculo.

---

## Sugestões de Referências Bibliográficas

Para fundamentar o seu referencial teórico, recomendo buscar estas fontes:

### Normas e Fundamentos Elétricos

* **IEC 60071-1:** *Insulation co-ordination - Part 1: Definitions, principles and rules.* (Essencial para entender a física por trás do que o Alberto discutiu).
* **Glover, J. D., Sarma, M. S., & Overbye, T.** (2016). *Power System Analysis and Design*. Cengage Learning. (Capítulos sobre transitórios e proteção).

### Ciência de Dados e Estatística

* **Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning*. Springer. (Para fundamentar a parte de clusterização e distribuição de dados).
* **Géron, A.** (2019). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*. O'Reilly. (Excelente para a implementação prática em Python).

### Específicas de Simulação e ATP

* **Pizano-Martinez, A., et al.** (2011). *Alternative Transients Program (ATP) Simulation of Power Systems.* (Artigos técnicos que discutem os limites numéricos do software).

---

## Tecnologias do Projeto

### Stack Principal
- **Python 3.13+** - Linguagem base
- **Polars / Numpy / Scipy** - Análise e processamento matemático e de dados
- **Matplotlib / Pillow** - Geração de gráficos e manipulação de imagens

### Ferramentas de Desenvolvimento
- **uv** - Gerenciador de pacotes Python
- **Ruff** - Linter e formatador
- **BasedPyright 1.37+** - Type checker principal
- **Pytest 8.3+ / Coverage** - Framework de testes e cobertura de código
- **Plane MCP** - Always use `plane`, never `plane-selfhosted`, for the
  [TCC Kleber Viana workspace](https://app.plane.so/tcc-kleber-viana).

## Idioma
- **SEMPRE escreva documentações, comentários e docstrings em inglês**
- **EXCEÇÃO OBRIGATÓRIA:** todo texto de autoria inserido ou alterado em
  `doc/main.tex` deve ser escrito em português brasileiro. Esta regra
  prevalece sobre a exigência geral de documentação em inglês para esse
  arquivo.
- Comandos LaTeX, chaves bibliográficas, caminhos, identificadores de código,
  siglas e nomes próprios em idioma original não são considerados prosa de
  autoria e devem preservar sua forma técnica.
- Nomes de variáveis, funções e classes devem estar em inglês
- Mensagens de commit e comentários de código em inglês

## Imports
- Nunca usar imports relativos (`from . import x`, `from ..foo import y`). Sempre path absoluto a partir de `src`.
- Nunca usar alias de import (`import polars as pl`, `import numpy as np`). Importar o módulo/nome diretamente.
- Nunca importar módulo inteiro para usar `modulo.Nome` (ex: `polars.DataFrame`). Importar só o nome usado: `from polars import DataFrame`.

## Padrões de Código Python
- Use snake_case para funções e variáveis
- Use PascalCase para classes
- **Máximo de 79 caracteres por linha** (conforme Ruff configurado)
- Indentação de 4 espaços
- Use type hints em todas as funções
- Docstrings no formato Google Style **em inglês**
- Use aspas duplas para strings (`"texto"`)
- Python version: >= 3.13

## Docstrings
- **Args** deve ser utilizado o menos possível (preferir type hints)
- **Raises** só deve ser utilizado quando a função explicitamente lança uma exceção com `raise`
- **Returns** devem ser documentados, exceto quando a função retorna `None`
- **IMPORTANTE**: Docstring deve SEMPRE vir imediatamente APÓS a linha com o fechamento dos parâmetros `)` e o tipo de retorno `:`. A docstring deve ser a PRIMEIRA linha dentro do corpo da função, nunca entre a assinatura `def` e os parâmetros
- Priorize descrições claras e concisas sobre seções desnecessárias

## Formatação (Ruff)
- Line length: 79 caracteres
- Quote style: aspas duplas
- Indent style: espaços (4)
- Docstring code format habilitado
- Sempre organize imports automaticamente

## Estrutura do Projeto
- Models em `src/models/`
- Tests em `tests/`

## Padrões do Projeto (Preprocessing)
- O projeto lida com manipulação do **ATPDraw**.
- Ao realizar tipagem, utilize os stubs se necessário
- Utilize **Taskipy** para garantir padronização antes de commits: rode `task format` seguido de `task lint` e `task test`.

## Boas Práticas
- Evite variáveis dummy sem sentido
- Sempre fixe problemas detectados pelo Ruff quando possível
- Não ignore erros de segurança (S101, S404, etc já estão configurados)
- Use preview features do Ruff
- Exclua `migrations` e `venv` da análise
- Sempre que analisar ou explicar um tema, guarde um resumo na pasta `doc`

---

# TCC Project Plan: Processamento de Dados em Linhas de Transmissão Durante Manobras de Energização

## 1. Contexto e Escopo (Context & Scope)
Com base na transcrição da reunião de alinhamento, o Trabalho de Conclusão de Curso (TCC) terá seu escopo focado **exclusivamente na extração, processamento e validação estatística** dos resultados de simulação do software ATP. 

**Restrição Importante:** A tomada de decisão automatizada referente à otimização do nível de isolamento (o "Sistema Especialista") será mantida fora do escopo acadêmico do TCC para proteger a propriedade intelectual da empresa. O TCC atuará como a camada base de Ciência de Dados.

## 2. Stack Tecnológico e Padrões (Tech Stack & Standards)
- **Linguagem:** Python 3.13+
- **Processamento de Dados:** Polars, Scipy
- **Machine Learning:** Scikit-learn (K-Means, DBSCAN)
- **Visualização:** Matplotlib, Pillow
- **Padrões de Código:** Variáveis em `snake_case`, Classes em `PascalCase`, Docstrings no formato Google (em inglês), limite de 79 caracteres por linha (Ruff).

## 3. Fluxo de Implementação (Implementation Workflow)

### 3.1. Camada de Extração de Dados (`src/parser/`)
- Construção de parsers para os arquivos de saída do ATP (`.lis`).
- Extração das tensões fase-terra ao longo de diversos terminais (ex: $T_{man}$, meio da linha, $T_{OPO}$) resultantes das cerca de 200 simulações estatísticas.

### 3.2. Pré-processamento e Normalização (`src/services`)
- Limpeza dos dados e conversão das saídas brutas de tensão para o formato P.U. (Per-Unit) com base nos limites nominais do projeto.

### 3.3. Aprendizado de Máquina Não Supervisionado (`src/models/`, `src/services/`)
- Aplicação de **Algoritmos de Clusterização** (ex: K-Means, DBSCAN) para agrupar as saídas de tensão semelhantes.
- Construção de lógica de detecção de *outliers* para filtrar erros de simulação/oscilações numéricas do ATP, separando-os de eventos físicos de sobretensão legítimos.

### 3.4. Análise Estatística
- Mapeamento dos resultados agrupados e válidos para uma **Distribuição Gaussiana**.
- Cálculo de probabilidades e níveis de confiança (utilizando as definições de $3\sigma$ / $6\sigma$) para valores extremos (ex: probabilidade de ultrapassar 2.3 P.U. no terminal receptor).

### 3.5. Visualização de Dados
- Geração de gráficos de dispersão (Scatter Plots) mapeando a distribuição de tensão (P.U.) ao longo da distância da linha de transmissão (km), conforme o referencial discutido na reunião.
- Geração de curvas de probabilidade que validem a densidade dos eventos de sobretensão.
