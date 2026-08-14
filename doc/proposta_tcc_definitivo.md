**Proposta de Trabalho de Conclusão de Curso (TCC)**  
**1. Título Sugerido**  
**Detecção de Anomalias e Análise Probabilística em Manobras de Energização de Linhas de Transmissão Utilizando ** **Machine** ** Learning**  
**2. Delimitação do Tema**  
O trabalho foca na interpretação de resultados de sobretensão transitória, gerados através de simulações estatísticas (dados sintéticos) no software **ATP (** **Alternative** ** ** **Transients** ** ** **Program** **)**. O foco está no processamento de dados sintéticos para identificar sobretensões críticas e diferenciar eventos físicos reais de instabilidades numéricas (erros de cálculo do software) durante manobras de energização de linhas de transmissão.  
**3. Problematização**  
Na engenharia de sistemas de potência, a coordenação de isolamento de equipamentos e linhas de transmissão depende de simulações exaustivas de manobras e surtos atmosféricos. O software ATP gera grandes volumes de resultados considerados como dados para nosso propósito (arquivos. lis) que contêm a resposta das tensões das três fases (A, B e C). No entanto, a análise manual desses dados é lenta e propensa a erros.  
O problema central reside na presença de **outliers** (valores atípicos) ou determinar a real probabilidade de acontecer na pratica um determinado valor máximo calculado, que irá influenciar diretamente na definição do nível de isolamento de linha: como determinar se um pico de tensão máxima é um risco real de falha no isolador ou apenas um "ruído" numérico do simulador? A falta de uma ferramenta automatizada para classificar esses eventos gera incerteza no dimensionamento, podendo elevar desnecessariamente os custos de projeto.  
**4. Objetivos**  
***4.1 Objetivo Geral***  
Desenvolver um modelo computacional em **Python** capaz de automatizar a extração, o tratamento estatístico e a classificação de dados de transitórios eletromagnéticos, utilizando algoritmos de  **Machine** ** Learning** para a detecção de anomalias.  
***4.2 Objetivos Específicos***  
- Implementar um *parser* para extração de dados brutos de arquivos estatísticos do ATP.  
- Aplicar a **Distribuição Gaussiana** com fixação de desvio padrão (3\sigma) para normalizar os resultados entre diferentes máquinas de cálculo.  
- Utilizar algoritmos de **Clusterização** (como K-Means ou DBSCAN) para agrupar comportamentos de onda e isolar outliers.  
- Calcular o nível de confiança e a probabilidade de ocorrência de sobretensões extremas.  
**5. Justificativa**  
A integração de Ciência de Dados na Engenharia Elétrica permite uma **Otimização de Ativos**. Para a empresa, isso se traduz em segurança técnica (confiabilidade) e otimização de investimento, para reduzir o nível de isolamento onde o risco estatístico é desprezível, gerando economia de milhões em infraestrutura. Para o campo da Engenharia de Software, o projeto demonstra a aplicação de IA em sistemas críticos e no tratamento de dados complexos de engenharia.  
**6. Metodologia (Roteiro Técnico)**  
1. **Coleta de Dados:** Geração de base de dados sintética (mínimo de 200 simulações por cenário) via ATP.  
2. **Pré-processamento:** Limpeza de dados e aplicação da regra de 3\sigma para garantir a integridade estatística.  
3. **Desenvolvimento do Modelo:** * Criação de uma "Nuvem de Pontos" (Tensão x Local de monitoramento).  
- Treinamento de modelo não supervisionado para identificar grupos de manobras "normais".  
4. **Análise de Resultados:** Comparação entre a análise estatística tradicional do ATP e os *insights* gerados pelo modelo de Machine Learning.  
