# Design de Processamento e Validação Estatística de Dados do ATP

**Especificação:** `specs/features/atp-processamento-validacao/spec.md`  
**Status:** Rascunho

## Visão geral da arquitetura

```text
Configuração + diretório de entrada
        |
        v
Carregador/parser -> tabela normalizada de observações
        |
        +--> validação da qualidade dos dados
        +--> rótulos DBSCAN
        +--> rótulos K-Means
        +--> rótulos estatísticos/sigma
                    |
                    v
       comparação + resumos por terminal
                    |
                    v
     tabelas + gráficos + pacote JSON de metadados
```

A implementação deve preservar os limites atuais dos serviços e adicionar uma
pequena camada de orquestração e geração de relatórios. Não deve introduzir
banco de dados nem serviço web.

## Análise de reutilização

| Componente existente | Localização | Reutilização |
|---|---|---|
| Parser do ATP e modelos Pydantic | `src/parser/` | Estender a validação apenas onde as fixtures revelarem lacunas |
| Carregador de diretório e extração P.U. | `src/services/preprocessing.py` | Reutilizar como base da tabela de entrada |
| Primitivas DBSCAN/K-Means | `src/services/clustering.py` | Adicionar validação e semântica estável aos rótulos |
| Ajuste Gaussiano e tabela sigma | `src/services/statistics.py` | Estender com resumos empíricos e tratamento de variância nula |
| Gráficos existentes | `src/services/visualization.py` | Reutilizar e tornar a geração configurável |
| Orquestração do script | `main.py` | Extrair pontos de configuração e geração de relatórios |

## Componentes e interfaces

### Configuração da análise

- **Localização:** `src/services/pipeline.py` ou módulo próprio de configuração.
- **Objetivo:** Representar caminho de entrada, codificação, tensão-base,
  terminais, política de fase, parâmetros de clusterização, limiar e diretório
  de saída.
- **Contrato:** A configuração deve ser serializável e validar tensão positiva,
  política de fase suportada e parâmetros válidos dos algoritmos.

### Validação da qualidade dos dados

- **Localização:** `src/services/validation.py`.
- **Objetivo:** Retornar problemas estruturados e uma tabela de observações
  limpa.
- **Contrato:** Nunca converter valores não finitos silenciosamente; registrar
  arquivo de origem, simulação, terminal e fase quando disponíveis.

### Resumo estatístico

- **Localização:** `src/services/statistics.py`.
- **Objetivo:** Adicionar excedência empírica, status sigma e saídas Gaussianas
  protegidas ao ajuste existente.
- **Contrato:** O resumo deve informar explicitamente amostra insuficiente ou
  variância nula, em vez de produzir probabilidades indefinidas.

### Comparação dos métodos

- **Localização:** `src/services/clustering.py` e, se necessário, um módulo de
  comparação.
- **Objetivo:** Alinhar rótulos DBSCAN, K-Means e sigma pela identidade da
  observação.
- **Contrato:** A saída deve conter rótulos dos algoritmos, quantidade de
  concordâncias e status de anomalia candidata, sem afirmar causalidade física.

### Executor reprodutível e gerador de artefatos

- **Localização:** `src/services/pipeline.py` e `main.py`.
- **Objetivo:** Executar todas as etapas e salvar tabelas, gráficos e
  metadados.
- **Contrato:** Não usar caminho absoluto; persistir todos os parâmetros e
  contagens.

## Modelo de dados

A tabela normalizada de observações mantém os campos atuais:

```text
source_file, simulation, terminal, phase, value_pu, time
```

A tabela analítica adiciona:

```text
dbscan_cluster, kmeans_cluster, sigma_flag,
method_agreement, anomaly_candidate, anomaly_reasons
```

A tabela de resumo contém, por terminal e fase:

```text
n_total, n_valid, n_outliers, mean, std, sigma_3_threshold,
empirical_exceedance, gaussian_exceedance, validation_status
```

Os metadados contêm configuração, horários UTC de início e fim, versões do
Python e dos pacotes, nomes dos arquivos de entrada, hashes dos arquivos
quando possível, quantidades de linhas e nomes dos artefatos.

## Estratégia de erros

| Cenário | Tratamento |
|---|---|
| Diretório inexistente ou sem arquivos | Lançar erro claro de entrada/configuração |
| Arquivo individual corrompido | Registrar o problema; o modo estrito decide se a execução para |
| Terminal/fase selecionado sem dados | Produzir status vazio explícito; não ajustar distribuição |
| Parâmetros inválidos | Validar antes da análise e lançar erro claro |
| Variância nula | Marcar cauda Gaussiana como indisponível ou determinística, conforme política documentada |
| Diretório de saída existente | Exigir política explícita de sobrescrita e registrá-la |

## Decisões técnicas

- Manter DBSCAN por terminal, pois o código atual já evita misturar
  distribuições de terminais.
- Manter a seleção de fase explícita; o comportamento padrão não deve agrupar
  A, B e C silenciosamente.
- Tratar outliers como anomalias candidatas e preservá-los nas saídas brutas e
  anotadas; somente dados válidos alimentam o ajuste Gaussiano.
- Usar configuração determinística no K-Means (`random_state`) e persistir
  todos os parâmetros do modelo.

