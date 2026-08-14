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
