# Estruturação das observações

## Status

**Validando.** Observation table implemented; experimental-unit and mapping validation remain open.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Check source file, simulation, terminal, phase, voltage, and time mappings against independently checked source records for the selected cases.
- [ ] Document the observation unit, uniqueness and completeness rules, and treatment of multiple files and scenarios.
- [ ] Describe the table as scalar voltage maxima in the methodology, and state the limits of any conclusions about waveforms.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Analisar todas as fases e os cenários relevantes](../pendente/02_fases_e_cenarios.md)

## Como foi feito

A função `extract_maxima_dataframe` transforma a saída estruturada do parser
em uma tabela Polars. Cada linha identifica o arquivo de origem, o número da
simulação, o terminal, a fase, o valor máximo em P.U. e o instante do máximo.
São mantidas apenas as grandezas fase-terra dos terminais configurados.

A estrutura final contém as colunas `source_file`, `simulation`, `terminal`,
`phase`, `value_pu` e `time`, com tipos definidos explicitamente. Isso permite
rastrear cada resultado até sua simulação e seu arquivo de origem.

## Avaliação de validade

A modelagem tabular é adequada para análise de máximos de sobretensão e está
alinhada aos objetivos atuais do pipeline. Ela não representa a forma de onda
completa. Consequentemente, o software agrupa valores máximos, e não
“comportamentos de onda” no sentido temporal. Essa diferença deve aparecer com
clareza na metodologia do TCC.

## Evidências e validação realizada

- Implementação: `src/services/preprocessing.py`.
- Testes de extração, filtro e esquema: `tests/test_preprocessing.py`.
- Artefato verificável: `raw_observations.csv` em cada pacote de resultados.

## Critério de manutenção

Se o escopo passar a incluir formas de onda, será necessário criar outra
estrutura contendo séries temporais ou atributos extraídos delas. Isso não deve
ser apresentado como já realizado pela tabela atual de máximos.

