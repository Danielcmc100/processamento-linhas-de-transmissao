# Qualidade e testes do software

## Status

**Validando.** Automated checks exist; verification of the scientific requirements remains open.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Map the final methodological requirements to checks with independently established expected results, including representative experimental cases.
- [ ] Run the configured quality checks on the code revision used for the thesis and retain dated commands and outputs.
- [ ] Document which requirements the evidence verifies and which scientific claims require experimental or technical validation beyond software tests.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Redigir os capítulos finais](../pendente/07_capitulos_finais.md)

## Como foi feito

O projeto usa Ruff para lint e formatação, BasedPyright para tipos e Pytest para
testes. Há testes específicos para parser, pré-processamento, validação,
estatística, clusterização, comparação, configuração, pipeline, relatórios e
visualizações.

## Avaliação de validade

Na revisão de 3 de setembro de 2026:

- o Ruff foi aprovado sem erros;
- o BasedPyright informou zero erros, avisos ou notas;
- os 94 testes foram aprovados;
- a cobertura de `src` e `main.py` atingiu 95%.

Essas evidências dão boa confiança sobre o comportamento codificado e a
proteção contra regressões. Elas não validam hipóteses estatísticas nem a
interpretação elétrica dos resultados, pois testes de software confirmam que o
código faz o especificado, não que a especificação científica seja correta.

## Evidências

- Configuração das ferramentas: `pyproject.toml`.
- Suíte: pasta `tests/`.
- Comandos padronizados: `task lint`, `task typecheck` e `task test`.

## Manutenção necessária

Novos testes devem acompanhar o protocolo final, principalmente casos
multifásicos, arquivos `.lis` alternativos, dados rotulados e verificações dos
indicadores publicados no TCC.

