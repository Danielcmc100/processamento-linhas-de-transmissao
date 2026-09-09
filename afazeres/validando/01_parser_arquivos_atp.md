# Parser dos arquivos ATP

## Status

**Validando.** Parser implemented; source-data fidelity still requires a documented audit.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Compare extracted headers, run identifiers, signed maxima, and times against independently checked ATP output samples from the thesis cases.
- [ ] Reconcile declared NENERG, extracted runs, and table lengths; record supported layouts and the treatment of incomplete or unsupported files.
- [ ] Attach the audit results and describe the supported extraction scope in the methodology.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Analisar todas as fases e os cenários relevantes](../pendente/02_fases_e_cenarios.md)

## Como foi feito

O módulo `src/parser` lê o conteúdo textual dos arquivos `.lis` e extrai:

- quantidade declarada de simulações (`NENERG`);
- configuração das chaves estatísticas;
- cabeçalhos das variáveis monitoradas;
- tempos de chaveamento de cada execução;
- máximos de tensão e seus instantes de ocorrência.

Os dados são convertidos em modelos Pydantic, como `LisParseResult`,
`SimulationRun` e `MaximaData`. A leitura em lote é realizada recursivamente
por `load_directory`.

## Avaliação de validade

A implementação é coerente com a estrutura dos arquivos ATP disponíveis e o
teste com o arquivo representativo confirma a associação básica entre
cabeçalhos, simulações, máximos e tempos. Entretanto, o parser depende de
marcadores textuais e da posição das tabelas. Portanto, sua validade ainda é
restrita às variantes de `.lis` conhecidas.

## Evidências e validação realizada

- Implementação: `src/parser/__init__.py` e `src/parser/models.py`.
- Integração: `src/services/preprocessing.py`.
- Testes: `tests/test_parser.py` e `tests/fixtures/representative.lis`.
- Historical assessment: the previous review reported passing software tests.

## Limitações que devem ser acompanhadas

É recomendável manter amostras de diferentes versões e configurações do ATP
como testes de regressão. Arquivos truncados, seções ausentes e alterações no
layout devem produzir erros explicativos, em vez de falhas genéricas durante a
separação do texto.

