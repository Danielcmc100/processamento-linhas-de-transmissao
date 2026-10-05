# Plano detalhado de preparação para a defesa

Este documento converte em ações as recomendações de preparação para a defesa
que não foram alteradas diretamente no manuscrito. A inclusão de uma ação
neste plano não significa que ela já tenha sido executada.

## 1. Contribuição e limites que devem orientar a defesa

A contribuição deve ser apresentada como **detectar e organizar candidatos
para investigação técnica posterior**. O sistema processa arquivos
estatísticos do ATP, preserva a rastreabilidade das observações e aplica
análises descritivas, probabilísticas e métodos para identificar candidatos
discrepantes. Não se deve afirmar que os métodos identificam definitivamente
erros numéricos do ATP, comprovam eventos físicos, removem dados
automaticamente ou determinam nível de isolamento.

O manuscrito registra 204.300 observações aceitas em dez arquivos SRPI/CRPI,
com 50, 100, 200, 1.000 e 10.000 simulações por cenário. Os cinco casos
selecionados para revisão técnica permanecem não resolvidos: faltam formas de
onda, repetição sob passo de integração menor e revisão por profissional
elétrico independente qualificado. Na defesa, separe quatro camadas:

1. **Validade dos dados:** extração, identidade, completude, normalização e
   limpeza no escopo auditado.
2. **Cálculo estatístico:** estatísticas e probabilidades calculadas segundo
   as definições metodológicas.
3. **Comportamento dos detectores:** resposta a perturbações sintéticas e
   variações de parâmetros nas condições efetivamente testadas.
4. **Interpretação elétrica/causal:** permanece não resolvida para os
   candidatos revisados; não é demonstrada por testes de software ou métricas
   sintéticas.

Não use êxito em uma camada como prova automática de outra. A concordância do
parser com pontos de verificação sustenta a fidelidade desses pontos, mas não
confirma a causa elétrica de um máximo.

## 2. Matriz objetivo–evidência–conclusão

Prepare uma tabela de uma página com uma linha por objetivo específico. Toda
afirmação quantitativa deve apontar para seção, tabela, figura ou artefato de
origem. A matriz abaixo é um roteiro para a preparação e não substitui a
conferência do manuscrito e dos dados atuais.

| Objetivo | Evidência a mostrar | Conclusão permitida | Limite a declarar |
|---|---|---|---|
| Extrair dados do ATP | Auditorias do parser, checkpoints independentes, contagens e relatório de validação | Parser validado para os leiautes e arquivos cobertos | Não é estimativa de erro para todo leiaute futuro nem auditoria independente de cada célula |
| Estruturar e rastrear observações | 204.300 linhas; chave por arquivo, simulação, terminal e fase; testes de completude e unicidade | Base aceita preserva identidade e completude no escopo declarado | Outros arquivos/cenários exigem validação própria |
| Converter para P.U. e limpar | Base de 112677 V, pontos conferidos, reconciliação de médias e testes de falhas | Conversão e regras de limpeza verificadas para fontes declaradas | A validação numérica individual usa pontos de verificação; não reconstrói formas de onda |
| Descrever estatisticamente | Resumos de 90 combinações e diagnóstico de distribuição | Distribuições e diferenças entre grupos foram quantificadas | Rejeição de normalidade limita inferências gaussianas |
| Estimar excedência | Contagens empíricas, intervalos de Wilson e reconciliação com ATP | Não houve excedência observada de 2,3 P.U. na amostra aceita; incerteza reportada | Probabilidade empírica zero não prova probabilidade populacional exatamente zero |
| Aplicar detectores | Comparação 3σ, MAD, distância K-Means e ruído DBSCAN | Métodos geram evidências/candidatos explícitos e podem divergir | Rótulo de cluster ou ruído não implica erro nem causa física |
| Comparar métodos | Benchmark sintético, sensibilidade e comparação no grupo de referência | Há medidas do comportamento nas intervenções/configurações testadas | Não é acurácia para erros ATP reais nem generaliza automaticamente a todos os grupos |
| Integrar/reproduzir o fluxo | Manifesto, comandos, hashes e artefatos derivados | Fluxo integrado executado para as dez fontes declaradas | Pacote incompleto quanto à interpretação elétrica independente |

### Como usar a matriz

- Faça cada slide de resultado responder a um objetivo, em vez de apenas
  acumular gráficos.
- Junto aos números, informe cenário, tamanho amostral, terminal, fase e regra
  de comparação.
- Diga se uma conclusão é descritiva, exploratória ou inferencial.
- Ao responder “o objetivo foi cumprido?”, diga primeiro o que a evidência
  demonstra e depois o limite. Não force uma resposta binária se o manuscrito
  qualifica o objetivo como parcial ou condicionado.

## 3. Gaussianidade, probabilidade e regra de $3\sigma$

### Mensagem essencial

A distribuição configurada para os instantes de chaveamento **não implica**
que os máximos de tensão resultantes tenham distribuição normal. O manuscrito
reporta rejeição da normalidade em 88 dos 90 grupos pelo teste
Anderson--Darling a 5%. Assim, a probabilidade empírica de excedência é o
resultado principal; a curva gaussiana é comparação qualificada, não
premissa universal nem substituto dos dados observados.

No grupo de referência $T_{OPO}$/fase A/$N=10.000$, o manuscrito relata
assimetria e excesso de curtose distintos para CRPI e SRPI, além de rejeição
de normalidade. A cauda gaussiana para 2,3 P.U. é numericamente pequena, mas
isso não torna adequado o ajuste: concordância em um limiar específico não
valida a distribuição inteira nem outros limiares/grupos.

O $3\sigma$ também depende de uma distribuição aproximadamente normal para
sua interpretação usual. No grupo de referência detalhado, ele não sinalizou
pontos enquanto o MAD sinalizou candidatos. Apresente essa discordância como
resultado, sem eleger nenhum detector como verdade de referência.

### Preparação dos slides

- Mostrar que 88/90 grupos rejeitaram normalidade, com teste e nível de
  significância identificados.
- Usar ao menos um histograma e gráfico quantil--quantil do grupo de
  referência, sem sugerir que a inspeção visual substitui o diagnóstico.
- Ao exibir estimativas empírica e gaussiana, identificar qual é primária e
  informar a adequação do ajuste.
- Explicar que “zero eventos observados” significa zero na amostra, com
  intervalo de confiança; não significa probabilidade populacional
  absolutamente nula.
- Explicar que a comparação gaussiana permite qualificar uma hipótese usual,
  em vez de assumir normalidade sem teste.

### Perguntas prováveis

**Por que usar $3\sigma$ se a normalidade foi rejeitada?** Como indicador
comparativo/preliminar, com aplicabilidade qualificada; não como regra
decisória universal. A rejeição e a divergência com MAD são reportadas, e
nenhum candidato é removido automaticamente.

**A probabilidade de exceder 2,3 P.U. é zero?** Não houve excedências na
amostra aceita. A estimativa empírica é zero para essa amostra e o intervalo
de Wilson expressa incerteza; isso não prova probabilidade populacional
exatamente nula.

**Se a cauda gaussiana também é minúscula, por que a rejeição importa?** A
semelhança em um limiar não valida o formato inteiro da distribuição, nem
garante outras caudas ou outros grupos.

## 4. Benchmark sintético e análise de sensibilidade

O benchmark introduz perturbações controladas em cópias dos dados. Ele mede
se os métodos recuperam as alterações conhecidas e quantos pontos limpos
sinalizam para as famílias, intensidades, taxas de contaminação e partição
usadas. Os rótulos são verdadeiros para a intervenção sintética definida;
não são rótulos de erro numérico real do ATP.

A divisão por bloco de simulação mantém fases e terminais de uma execução no
mesmo subconjunto, reduzindo vazamento entre desenvolvimento e avaliação. A
escala, os limiares e as calibrações são ajustados no desenvolvimento. A
apresentação de precisão, revocação, $F_1$ e taxa de falsos positivos deve
explicar essa configuração antes de interpretar os valores.

A sensibilidade mede se o conjunto de candidatos muda sob a grade de
parâmetros escolhida. Jaccard igual a 1 nas réplicas relatadas significa que
os conjuntos comparados foram idênticos sob aquelas variações; não significa
que os pontos são verdadeiros erros ou que o método é acurado. O manuscrito
restringe o resultado ao grupo de referência e à grade testada.

### Roteiro para explicar uma tabela de benchmark

1. Defina a intervenção e informe que a base original foi preservada.
2. Identifique família (pontual, contextual ou coletiva) e taxa de
   contaminação.
3. Explique a divisão desenvolvimento/avaliação e onde foram ajustados escala
   e limiares.
4. Leia uma linha: verdadeiros/falsos positivos, precisão, revocação, $F_1$ e
   taxa de falsos positivos.
5. Diga exatamente o que as métricas demonstram para aquela intervenção.
6. Declare que isso não valida diagnóstico de erros ATP reais nem generaliza
   para todos os grupos.

### Perguntas prováveis

**O benchmark prova que o detector encontra erros do ATP?** Não. Mede a
detecção das intervenções sintéticas declaradas, na partição, grupo e
configurações testados.

**Jaccard 1 significa acurácia perfeita?** Não. Indica estabilidade de
identidade entre os conjuntos comparados naquela grade, não correspondência
com causas verdadeiras.

**Por que DBSCAN teve mais falsos positivos na condição limpa?** Apresente a
taxa observada e relacione-a à calibração por densidade e às limitações do
método nas condições testadas. Não omita o resultado: ele evidencia custos e
limites da configuração.

## 5. Demonstração reprodutível

Prepare uma demonstração curta e ensaiada, com artefatos já gerados. Evite
depender de ATP ou rede ao vivo. Uma execução ao vivo pode falhar por
ambiente, duração ou dependências; além disso, a validação documentada
registra indisponibilidade do runtime ATP para repetir simulações com passo
menor.

### Caminho de uma observação

1. Escolha um registro representativo do grupo CRPI/SRPI, terminal
   $T_{OPO}$, fase A, $N=10.000$, de preferência ligado à revisão técnica.
2. Mostre cenário, arquivo, hash, simulação, terminal, fase, máximo com
   sinal, valor P.U. e instante.
3. Mostre associação ao registro e normalização pela base fase-terra de
   112677 V.
4. Mostre, para o mesmo registro, indicadores $3\sigma$, MAD, distância
   K-Means e estado DBSCAN, incluindo aplicabilidade e limiares.
5. Apresente contexto da execução (outras fases e terminais), quando
   disponível, não apenas um ponto isolado.
6. Conclua corretamente: “candidato para investigação”, não “erro do ATP”.
7. Mostre que evidência ainda seria necessária para atribuir causa: forma de
   onda, repetição com passo menor e revisão elétrica independente.

### Kit local

- PDF final e slides exportados localmente.
- Tabelas e figuras finais citadas em `doc/main.tex`.
- `results/defense-evidence/v1/reproducibility_manifest.json` e
  `package_status.json`.
- Relatórios de parser, estrutura de observações, conversão P.U. e limpeza,
  além dos registros em `doc/evidence/`.
- Comandos exatos de reprodução, versão/configuração de código declaradas no
  manifesto e cópias locais das evidências necessárias.
- Capturas/saídas em PDF caso terminal ou ambiente não estejam disponíveis.
- Backup acessível da apresentação e artefatos, respeitando restrições de
  confidencialidade.

Confirme com a orientação quais dados podem ser compartilhados publicamente e
quais devem permanecer restritos à defesa. Não exponha arquivos proprietários
ou dados do ONS/empresa sem autorização.

## 6. Revisão elétrica independente: plano e contingência

### Se for possível concluir antes da defesa

- Solicite revisão a profissional qualificado e independente do
  desenvolvimento do detector.
- Priorize os casos selecionados para cobrir concordância, discordância,
  escore elevado, proximidade de limiar e controle não sinalizado.
- Disponibilize saída original e identidade completa, condições de
  chaveamento, outras fases/terminais, formas de onda e parâmetros do modelo.
- Quando possível, repita condições iniciais e chaveamento equivalentes com
  passos de integração menores e registre as diferenças.
- Para cada caso, registre revisor, data, evidências, justificativa e uma
  categoria: defeito de dados, artefato numérico suspeito, extremo
  fisicamente plausível ou não resolvido.
- Atualize manuscrito, tabelas e manifesto em conjunto. Concordância entre
  algoritmos não é, sozinha, atribuição de causa.

### Se não for possível

- Apresente a lacuna como limitação concreta, não como trabalho concluído.
- Diga que o pipeline realiza triagem rastreável e organiza candidatos, mas
  não diagnóstico causal.
- Não trate a ausência de formas de onda como evidência a favor ou contra uma
  hipótese física.
- Separe a indisponibilidade do runtime ATP para repetição da ausência de
  revisor independente; são limitações diferentes.
- Descreva a revisão como validação pendente necessária, e não como extensão
  já resolvida.

### Resposta curta para a banca

“O método não determina se o ponto é erro numérico ou evento físico. Ele
combina evidências estatísticas e de clusterização para localizar e organizar
candidatos rastreáveis. A atribuição causal requer inspeção da forma de onda,
repetição numérica e revisão elétrica independente, que não foram concluídas
neste estudo.”

## 7. Conferências formais do manuscrito

Confirme requisitos com secretaria, manual institucional e orientação:

- **Banca:** substituir “A definir” nos campos de primeiro e segundo membro,
  incluindo titulação e instituição, quando oficialmente confirmados
  (`doc/main.tex`, linhas 160–165).
- **Data:** confirmar se “28 de Novembro de 2026” é a data correta antes de
  alterar (`doc/main.tex`, linha 154).
- **Resumo em português:** revisar o trecho colorido em vermelho (por volta
  da linha 399), remover marca editorial e assegurar que descreve resultados
  concluídos, não só expectativas.
- **Abstract:** conferir equivalência com o resumo revisado, tempo verbal,
  palavras-chave e terminologia técnica.
- **Titulações/afiliação:** confirmar grafia, instituição e titulações da
  orientação e dos membros da banca.
- **Folha de aprovação:** confirmar procedimento para assinaturas e momento
  de inclusão.
- **Ficha catalográfica:** o código indica obtenção da ficha definitiva após
  defesa; confirmar requisitos diferentes para cópia de defesa e final.
- **Dedicatória/epígrafe:** confirmar que os textos de exemplo são desejados
  pelo autor e adequados à versão final.
- **Listas pré-textuais:** conferir figuras, tabelas, siglas e símbolos com o
  conteúdo e manual institucional.
- **PDF final:** revisar paginação, referências cruzadas, tabelas, legibilidade
  das figuras, metadados e ausência de marcações editoriais.

Não preencha informações acadêmicas desconhecidas por suposição. Data, nomes,
titulações, assinaturas e requisitos de ficha devem ser confirmados com fonte
institucional.

## 8. Sequência sugerida da apresentação

Adapte ao tempo permitido pela banca, sem perder a sequência lógica:

1. Problema: volume de saídas ATP e necessidade de triagem organizada e
   reprodutível.
2. Pergunta e escopo: identificar discrepâncias e organizar candidatos; não
   diagnosticar causa nem recomendar isolamento.
3. Sistema e dados: cenário, modelo, linha, manobra, SRPI/CRPI e unidade de
   observação; esclarecer que a base contém máximos, não formas de onda.
4. Pipeline: extração, identidade, conversão P.U., integridade, estatística,
   probabilidade e detectores.
5. Validação de dados: parser, completude e conversão, com escopo exato das
   auditorias.
6. Resultados estatísticos: excedência empírica, incerteza e adequação
   gaussiana.
7. Candidatos: comparação de $3\sigma$/MAD/K-Means/DBSCAN, incluindo
   concordâncias e discordâncias.
8. Benchmark e estabilidade: intervenções sintéticas e limite de
   generalização.
9. Limitações: casos não resolvidos e evidência elétrica ausente.
10. Conclusão: contribuição demonstrada, objetivos e próximos passos.

Não tente apresentar as 90 combinações em detalhe. Use visão geral compacta,
aprofunde um grupo representativo e mantenha tabelas completas no apêndice dos
slides.

## 9. Perguntas adicionais para ensaio

### Problema e contribuição

- Qual trabalho manual ou risco de inconsistência o pipeline reduz?
- Qual é a unidade de observação e por que não se tratou cada simulação como
  um único ponto?
- Qual parte é contribuição de Ciência da Computação e qual depende de
  Engenharia Elétrica?
- Por que o título menciona detecção de anomalias se a conclusão causal está
  não resolvida? Diferencie detecção de discrepância/candidato de diagnóstico
  da causa. Discuta eventual ajuste de título somente com a orientação.

### Dados e generalização

- São medições reais? Não: são saídas simuladas, condicionadas ao cenário e
  modelo declarados.
- Os tamanhos amostrais são independentes ou aninhados? Use a ressalva do
  manuscrito; não assuma independência/aninhamento sem evidência.
- Por que SRPI e CRPI são analisados separadamente? As definições de
  chaveamento diferem.
- A validação de dez arquivos cobre qualquer saída ATP? Não; novos leiautes
  exigem validação.
- Máximos permitem concluir duração ou frequência do transitório? Não; isso
  exige séries temporais/formas de onda.

### Métodos e resultados

- Por que separar por cenário, linhagem, terminal e fase? Para não converter
  diferenças contextuais/sistemáticas em anomalias espúrias.
- Por que o maior centróide K-Means não significa anomalia? Centróides e
  rótulos descrevem grupos; a evidência usada é distância com limiar
  calibrado.
- O que significa DBSCAN não produzir candidatos? Resultado daquela regra e
  calibração, não prova de inexistência de valores relevantes.
- Por que não remover outliers antes da estatística? Um extremo pode ser
  fisicamente relevante; removê-lo pode esconder o caso a investigar.
- De onde vem o limiar 2,3 P.U. e qual evento foi contado? Responda com a
  justificativa documentada e o operador estrito $V_{pu}>v$; não improvise
  uma justificativa normativa ausente do trabalho.

### Reprodutibilidade

- O que os testes automatizados provam? Comportamento do software para
  contratos/casos testados, não validade física.
- Como se verifica a identidade das entradas? Hashes SHA-256 no pacote e
  manifesto.
- O que significa “independente” nas auditorias? Procedimento de
  extração/transcrição independente conforme descrito, não necessariamente
  revisão humana independente.
- O que falta para reproduzir em outra máquina? Dados autorizados, versões,
  configuração, comandos, código e ATP compatível quando for necessário
  executar o solver.

## 10. Checklist final

### Manuscrito

- [ ] Contribuição distingue candidatos de causas confirmadas.
- [ ] Limitações não dizem que análises já realizadas são “etapas seguintes”.
- [ ] Resumo e abstract descrevem resultados concluídos e a limitação
      principal, sem texto vermelho/comentários editoriais.
- [ ] Objetivos, resultados e conclusão têm o mesmo escopo e terminologia.
- [ ] Cada número dos slides aponta para tabela, figura, relatório ou
      artefato rastreável.
- [ ] Referências, legendas e elementos institucionais foram conferidos.

### Evidência

- [ ] Rejeição gaussiana apresentada com contexto do teste.
- [ ] Zero excedências acompanhado de denominador e incerteza.
- [ ] Benchmark sintético não descrito como acurácia em erros ATP reais.
- [ ] Jaccard/estabilidade não confundidos com acurácia.
- [ ] Nenhum candidato rotulado físico/numérico sem revisão independente.
- [ ] Limites dos dados de máximos e do escopo aparecem nos slides.

### Apresentação

- [ ] Demonstração ensaiada sem dependência de ATP ao vivo.
- [ ] PDF, slides, tabelas, manifesto e respostas disponíveis offline.
- [ ] Exemplo percorre observação com identidade e origem rastreáveis.
- [ ] Resposta para “o método encontra erros numéricos?” foi ensaiada.
- [ ] Compartilhamento dos artefatos foi autorizado.
- [ ] Tempo e apêndice de slides foram ensaiados com a orientação.

## 11. Arquivos do projeto para conferir

- `doc/main.tex`: manuscrito, metodologia, resultados, limitações e conclusão.
- `doc/defense_validation_plan.md`: plano de evidências e linguagem de
  aceitação.
- `specs/features/thesis-defense-evidence/validation.md`: estado de
  validação e bloqueio de repetição com ATP.
- `results/defense-evidence/v1/package_status.json`: camadas aceitas e
  lacuna de revisão técnica.
- `results/defense-evidence/v1/reproducibility_manifest.json`: proveniência
  e reprodução do pacote, conforme os campos nele registrados.
- `doc/parser_validation_report.md`,
  `doc/observation_structure_validation_report.md`,
  `doc/data_cleaning_validation_report.md` e `doc/evidence/`: evidências
  referidas no manuscrito.

Este plano orienta a preparação; confira números e conclusões nos artefatos
atuais antes de reutilizá-los em slides ou respostas.
