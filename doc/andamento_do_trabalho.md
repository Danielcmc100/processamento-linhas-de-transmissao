# Andamento do Trabalho

Data da avaliação: 3 de setembro de 2026.

## Situação atual

O trabalho está aproximadamente 65% concluído. A base do software encontra-se
em estágio avançado, enquanto a validação experimental e a redação dos
capítulos finais ainda representam as principais etapas pendentes.

## O que foi desenvolvido

- Leitura e extração automática dos arquivos `.lis` gerados pelo ATP.
- Estruturação dos valores máximos de tensão por simulação, terminal e fase.
- Conversão das tensões para valores por unidade (P.U.).
- Validação e limpeza dos dados antes da análise.
- Cálculo de média, desvio padrão e limite baseado na regra de três sigmas.
- Ajuste da distribuição Gaussiana e cálculo das probabilidades empírica e
  teórica de excedência.
- Aplicação dos algoritmos DBSCAN e K-Means.
- Comparação dos indícios de anomalia encontrados pelos diferentes métodos.
- Geração de gráficos, tabelas, arquivos de configuração e metadados para
  permitir a reprodução das análises.
- Processamento de conjuntos com 50, 100, 200, 1.000 e 10.000 simulações.
- Implementação de testes automatizados. Atualmente, os 94 testes são
  aprovados, sem erros de lint ou de verificação estática de tipos.
- Redação da introdução, da fundamentação teórica e do capítulo de modelagem
  do sistema elétrico.

## O que falta para concluir

1. Definir e justificar o protocolo experimental definitivo, incluindo os
   parâmetros utilizados no DBSCAN e no K-Means.
2. Ampliar a análise para as fases B e C e para os demais cenários relevantes,
   pois os resultados consolidados atuais consideram apenas a fase A de um
   cenário selecionado.
3. Verificar a adequação da distribuição Gaussiana por meio de diagnósticos e
   testes estatísticos apropriados.
4. Validar as anomalias com conhecimento técnico, inspeção dos casos do ATP ou
   dados controlados, evitando classificar automaticamente uma sobretensão
   elevada como erro numérico.
5. Comparar formalmente os resultados da regra de três sigmas, do DBSCAN e do
   K-Means.
6. Interpretar os resultados considerando o comportamento elétrico da linha e
   responder à questão de pesquisa.
7. Escrever os capítulos de metodologia e desenvolvimento, resultados e
   discussão, e conclusão.
8. Inserir no TCC as tabelas e figuras finais e realizar a revisão
   bibliográfica, textual e de formatação em LaTeX.

## Ponto de atenção

Nas execuções já consolidadas, o DBSCAN não classificou observações como
ruído. Entretanto, a regra combinada marcou aproximadamente metade das
observações como candidatas a anomalia, principalmente por pertencerem ao
grupo de maior centróide do K-Means. Pertencer ao agrupamento de maiores
tensões não significa, por si só, que uma observação seja um erro numérico.
Esse critério precisa ser revisto e validado antes de fundamentar as conclusões
do trabalho.

Em síntese, a implementação computacional está madura, mas a conclusão do TCC
depende principalmente da validação científica dos métodos, da execução do
plano experimental completo e da redação dos capítulos de análise.
