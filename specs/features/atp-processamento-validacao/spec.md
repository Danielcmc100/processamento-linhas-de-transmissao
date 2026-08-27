# Especificação de Processamento e Validação Estatística de Dados do ATP

**Status:** Rascunho  
**Fonte:** Objetivos do TCC em `doc/main.tex` e inspeção do repositório em
2026-08-14

## Problema

O projeto possui componentes isolados de processamento, mas ainda não prova
que a análise completa do ATP é reprodutível com dados representativos nem que
a classificação de anomalias é sustentada simultaneamente por evidências
estatísticas e de clusterização. Esta funcionalidade fecha essa lacuna,
preservando o limite do TCC: produz evidências analíticas auditáveis, não uma
decisão automatizada sobre o nível de isolamento.

## Avaliação da conclusão dos objetivos

| Objetivo | Evidência atual | Avaliação |
|---|---|---|
| Extrair dados estatísticos brutos do ATP | Parser e teste unitário existem | **Aparentemente concluído para o formato testado; validação com arquivos reais pendente** |
| Estruturar dados para máximos por fase | Modelos Pydantic e extração com Polars existem | **Aparentemente concluído para o esquema implementado** |
| Pré-processar e aplicar o critério de `3sigma` | Normalização P.U. e tabela sigma Gaussiana existem | **Parcialmente concluído; falta validação explícita de qualidade e normalidade** |
| Realizar análise probabilística de sobretensões | Probabilidades de cauda e gráfico de excedência existem | **Parcialmente concluído; faltam completar confiança e relatório empírico** |
| Aplicar K-Means e DBSCAN | Ambas as funções existem; DBSCAN é usado em `main.py` | **Parcialmente concluído; K-Means não está integrado nem testado** |
| Comparar resultados estatísticos e de clusterização | Não existe rotina ou relatório de comparação | **Não há evidência de conclusão** |
| Criar rotina integrada e reprodutível | `main.py` executa um script com caminho fixo | **Parcialmente concluído; faltam configuração, testes de integração e metadados** |

## Objetivos da funcionalidade

- [ ] Validar o parser e o carregador usando fixtures representativas de
  arquivos `.lis` do ATP.
- [ ] Tornar explícitos e reprodutíveis os dados de entrada e parâmetros dos
  modelos.
- [ ] Produzir evidências probabilísticas empíricas e Gaussianas com suas
  premissas documentadas.
- [ ] Integrar e testar K-Means e DBSCAN quando a comparação dos métodos for
  necessária.
- [ ] Classificar anomalias como candidatas analíticas, com razões rastreáveis,
  sem afirmar que a clusterização prova uma falha numérica do ATP.
- [ ] Gerar um pacote auditável de resultados contendo tabelas, figuras e
  metadados.

## Fora do escopo

| Item | Motivo |
|---|---|
| Otimização automática do isolamento | Explicitamente excluída do TCC |
| Recomendação de sistema especialista | Propriedade intelectual da empresa |
| Geração de simulações físicas no ATP | Esta funcionalidade consome saídas do ATP |
| Afirmação automática de que todo ruído do DBSCAN é erro numérico | Requer validação de domínio além da aprendizagem não supervisionada |

## Histórias de usuário e critérios de aceitação

### P1: Analisar e normalizar um conjunto de dados

Como pesquisador, quero converter um diretório de saídas do ATP em uma tabela
tipada e normalizada, para rastrear cada observação analisada à simulação,
terminal, fase, valor e instante correspondentes.

1. QUANDO arquivos `.lis` válidos forem fornecidos, ENTÃO o sistema DEVE
   analisar todas as execuções suportadas e agregar os máximos fase-terra.
2. QUANDO uma tensão-base e um conjunto de terminais forem fornecidos, ENTÃO o
   sistema DEVE normalizar os valores para P.U. e preservar os identificadores
   de origem.
3. QUANDO um arquivo estiver vazio, corrompido ou não possuir o terminal
   selecionado, ENTÃO o sistema DEVE reportá-lo ou ignorá-lo conforme uma
   política documentada e NÃO DEVE fabricar observações silenciosamente.

**Teste independente:** Executar o carregador sobre fixtures versionadas e
comparar quantidades de linhas, campos e valores normalizados com as saídas
esperadas.

### P1: Produzir evidências estatísticas e probabilísticas

Como pesquisador, quero resumos por terminal que combinem análise empírica e
Gaussiana, para discutir valores extremos com incerteza e premissas
quantificadas.

1. QUANDO um terminal possuir observações válidas, ENTÃO o sistema DEVE
   informar quantidade, média, desvio padrão amostral, limites sigma e
   probabilidades de cauda Gaussiana.
2. QUANDO um limiar como 2,3 P.U. for fornecido, ENTÃO o sistema DEVE informar
   a excedência empírica e a excedência segundo o ajuste Gaussiano, quando
   estimáveis.
3. QUANDO um terminal possuir observações insuficientes ou variância nula,
   ENTÃO o sistema DEVE retornar um resultado de validação documentado em vez
   de uma estimativa de cauda inválida.

**Teste independente:** Usar fixtures determinísticas com valores conhecidos e
verificar os cálculos de resumo e excedência.

### P1: Detectar e comparar anomalias candidatas

Como pesquisador, quero comparar em uma tabela os rótulos de DBSCAN, K-Means e
sigma, para que um outlier não seja interpretado com base em um único método.

1. QUANDO parâmetros de clusterização forem fornecidos, ENTÃO o sistema DEVE
   registrar algoritmo, parâmetros, rótulo do cluster e linha de origem para
   cada observação.
2. QUANDO uma observação for sinalizada por um ou mais métodos, ENTÃO o sistema
   DEVE expor concordâncias, discordâncias e um status não conclusivo de
   anomalia candidata.
3. QUANDO K-Means for solicitado com quantidade inválida de clusters ou linhas
   insuficientes, ENTÃO o sistema DEVE falhar com erro de validação claro.

**Teste independente:** Usar clusters sintéticos separados e pontos extremos
conhecidos para verificar rótulos, concordâncias e entradas inválidas.

### P1: Executar uma análise reprodutível

Como pesquisador, quero um comando configurável para executar o pipeline e
salvar os resultados, para regenerar as figuras e tabelas utilizadas no TCC.

1. QUANDO uma configuração especificar caminho de entrada, política de fase,
   tensão-base, terminais, parâmetros dos algoritmos e diretório de saída,
   ENTÃO o sistema DEVE executar sem caminhos específicos da máquina.
2. QUANDO a execução terminar, ENTÃO o sistema DEVE salvar tabelas analíticas,
   figuras, parâmetros, contagens e metadados de software e execução.
3. QUANDO uma entrada ou configuração obrigatória for inválida, ENTÃO o sistema
   DEVE falhar antes de produzir um pacote de resultados enganoso.

**Teste independente:** Executar duas vezes a mesma fixture e configuração e
comparar as tabelas determinísticas e os campos de metadados que devem ser
estáveis.

## Casos extremos

- Diretório vazio ou sem arquivos `.lis` correspondentes.
- `NENERG` ausente, cabeçalhos ausentes, execução truncada ou quantidades
  inconsistentes de valores e instantes.
- Máximos de tensão negativos e valores não finitos.
- Uma observação, menos observações que `min_samples` ou variância nula.
- Fases com distribuições materialmente diferentes.
- Terminais inexistentes na entrada.
- Nova execução em diretório de saída já existente.

## Rastreabilidade dos requisitos

| ID | Requisito | Prioridade | Status |
|---|---|---:|---|
| ATP-01 | Analisar e agregar arquivos `.lis` suportados | P1 | Em design |
| ATP-02 | Normalizar e preservar campos rastreáveis | P1 | Em design |
| ATP-03 | Validar qualidade dos dados e casos extremos | P1 | Pendente |
| ATP-04 | Produzir resumos Gaussianos, sigma e probabilidades empíricas | P1 | Em design |
| ATP-05 | Executar e registrar classificações DBSCAN e K-Means | P1 | Em design |
| ATP-06 | Comparar evidências estatísticas e de clusterização | P1 | Pendente |
| ATP-07 | Executar pipeline configurável e reprodutível | P1 | Pendente |
| ATP-08 | Salvar tabelas, figuras e metadados auditáveis | P1 | Pendente |
| ATP-09 | Preservar o limite de escopo do TCC | P1 | Verificado |

**Cobertura:** 9 requisitos no total; 7 mapeados para design/tarefas; 2
pendentes de detalhamento; nenhum requisito intencionalmente sem mapeamento.

## Critérios de sucesso

- Todos os gates versionados passam, incluindo o BasedPyright.
- Uma fixture representativa conclui o fluxo de ponta a ponta com quantidades
  determinísticas de linhas e artefatos de resultado.
- Toda anomalia do relatório possui evidências estatísticas e de clusterização
  registradas.
- O pacote gerado pode ser recriado a partir de sua configuração sem caminho
  específico de uma máquina.

