# Tarefas de Processamento e Validação Estatística de Dados do ATP

**Design:** `specs/features/atp-processamento-validacao/design.md`  
**Status:** Rascunho

## Plano de execução

### Fase 1 — Evidências e contratos

```text
T1 -> T2 -> T3
```

### Fase 2 — Serviços de análise

```text
             +-> T4 ->+
T3 ----------+-> T5 ->+-> T7
             +-> T6 ->+
```

### Fase 3 — Integração e evidências

```text
T7 -> T8 -> T9
```

## Detalhamento das tarefas

### T1: Adicionar fixtures representativas do parser e do carregador

- **Requisito:** ATP-01, ATP-02, ATP-03
- **Onde:** `tests/fixtures/`, testes do parser e do pré-processamento
- **Depende de:** Nenhuma
- **Concluída quando:** As fixtures cobrirem múltiplas execuções, fases,
  terminais, valores negativos e ao menos uma política para entrada corrompida
  ou vazia; quantidades esperadas e valores normalizados forem verificados.
- **Testes:** Testes unitários, no mesmo escopo.
- **Gate:** `uv run pytest tests/test_parser.py tests/test_preprocessing.py`

### T2: Definir configuração validada da análise

- **Requisito:** ATP-07
- **Onde:** `src/services/pipeline.py` ou módulo de configuração e testes
- **Depende de:** T1
- **Concluída quando:** A configuração validar caminhos, tensão-base, política
  de fase, terminais, parâmetros DBSCAN/K-Means, limiar e política de saída;
  além de ser serializável.
- **Testes:** Testes unitários para configurações válidas e inválidas.
- **Gate:** `uv run ruff check . && uv run pytest`

### T3: Adicionar validação estruturada da qualidade dos dados

- **Requisito:** ATP-03
- **Onde:** `src/services/validation.py` e testes
- **Depende de:** T1, T2
- **Concluída quando:** Valores não finitos, seleções ausentes, entradas
  inconsistentes e conjuntos vazios produzirem status estruturados e
  testáveis.
- **Testes:** Testes unitários para cada política de caso extremo.
- **Gate:** `uv run ruff check . && uv run pytest`

### T4: Estender resumos empíricos e estatísticos protegidos [P]

- **Requisito:** ATP-04
- **Onde:** `src/services/statistics.py`, `tests/test_statistics.py`
- **Depende de:** T3
- **Concluída quando:** Os resumos por terminal incluírem excedência empírica,
  excedência Gaussiana, limites sigma e status explícitos para amostra
  insuficiente ou variância nula.
- **Testes:** Testes unitários com valores determinísticos e casos extremos.
- **Gate:** `uv run ruff check . && uv run pytest tests/test_statistics.py`

### T5: Fortalecer DBSCAN e integrar rótulos K-Means testados [P]

- **Requisito:** ATP-05
- **Onde:** `src/services/clustering.py`, `tests/test_clustering.py`
- **Depende de:** T3
- **Concluída quando:** Entradas vazias, pequenas ou inválidas forem tratadas,
  os rótulos preservarem a identidade das linhas e ambos os algoritmos
  possuírem testes determinísticos.
- **Testes:** Testes unitários para clusters separados, ruído e parâmetros
  inválidos.
- **Gate:** `uv run ruff check . && uv run pytest tests/test_clustering.py`

### T6: Implementar comparação entre estatística e clusterização [P]

- **Requisito:** ATP-06
- **Onde:** `src/services/comparison.py`, `tests/test_comparison.py`
- **Depende de:** T3, T4, T5
- **Concluída quando:** Cada observação possuir rótulos dos métodos, quantidade
  de concordâncias, status de candidata e razões; sem afirmar causalidade
  física.
- **Testes:** Testes unitários para concordância, discordância e rótulos
  ausentes.
- **Gate:** `uv run ruff check . && uv run pytest tests/test_comparison.py`

### T7: Construir executor configurável de ponta a ponta [P]

- **Requisito:** ATP-07
- **Onde:** `src/services/pipeline.py`, `main.py` e testes de integração
- **Depende de:** T2, T3, T4, T5, T6
- **Concluída quando:** Um diretório de fixtures percorrer carregamento,
  análise, comparação e geração de gráficos sem caminho fixo da máquina.
- **Testes:** Teste de integração com diretórios temporários de entrada e saída.
- **Gate:** `uv run ruff check . && uv run pytest`

### T8: Gravar artefatos auditáveis de resultados

- **Requisito:** ATP-08
- **Onde:** gerador de relatórios/pipeline e testes de integração
- **Depende de:** T7
- **Concluída quando:** Dados brutos/anotados, tabelas de resumo, figuras,
  configuração, contagens e metadados de execução forem salvos e puderem ser
  regenerados.
- **Testes:** Existência de artefatos, esquema, conteúdo determinístico e
  política de sobrescrita.
- **Gate:** `uv run ruff check . && uv run pytest`

### T9: Corrigir tipagem e documentar evidências de validação

- **Requisito:** ATP-08, ATP-09
- **Onde:** `src/services/visualization.py`, estado do projeto e notas do TCC
- **Depende de:** T8
- **Concluída quando:** BasedPyright passar, limitações forem documentadas e o
  pacote de evidências for referenciado no fluxo do TCC.
- **Testes:** Gate completo de qualidade.
- **Gate:** `uv run ruff check . && uv run ruff format --check . && uv run basedpyright && uv run pytest`

## Matriz de rastreabilidade

| Requisito | Tarefas | Cobertura |
|---|---|---|
| ATP-01 | T1 | Completa |
| ATP-02 | T1 | Completa |
| ATP-03 | T1, T3 | Completa |
| ATP-04 | T4 | Completa |
| ATP-05 | T5 | Completa |
| ATP-06 | T6 | Completa |
| ATP-07 | T2, T7 | Completa |
| ATP-08 | T8, T9 | Completa |
| ATP-09 | T9 | Completa |

## Verificações pré-aprovação

### Granularidade

Cada tarefa possui um entregável principal, um limite de código e testes no
mesmo escopo quando há código novo ou alterado. **Aprovada.**

### Verificação de dependências

| Tarefa | Dependências declaradas | Predecessoras no diagrama | Resultado |
|---|---|---|---|
| T1 | Nenhuma | Nenhuma | Aprovada |
| T2 | T1 | T1 | Aprovada |
| T3 | T1, T2 | T2 | Aprovada |
| T4 | T3 | T3 | Aprovada |
| T5 | T3 | T3 | Aprovada |
| T6 | T3, T4, T5 | T3, T4, T5 | Aprovada |
| T7 | T2, T3, T4, T5, T6 | T6 | Aprovada |
| T8 | T7 | T7 | Aprovada |
| T9 | T8 | T8 | Aprovada |

### Co-localização dos testes

| Tarefa | Tipo de teste exigido | Testes incluídos | Resultado |
|---|---|---|---|
| T1 | Unitário | Sim | Aprovada |
| T2 | Unitário | Sim | Aprovada |
| T3 | Unitário | Sim | Aprovada |
| T4 | Unitário | Sim | Aprovada |
| T5 | Unitário | Sim | Aprovada |
| T6 | Unitário | Sim | Aprovada |
| T7 | Integração | Sim | Aprovada |
| T8 | Integração | Sim | Aprovada |
| T9 | Gate completo | Sim | Aprovada |

