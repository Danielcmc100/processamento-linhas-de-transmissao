# Conversão das tensões para P.U.

## Status

**Validando.** P.U. conversion implemented; the electrical base remains unverified.

## Scientific acceptance review — 2026-09-07

The implementation evidence below supports technical progress. Historical
claims about passing checks or PDF compilation were not rerun in this review
and do not constitute scientific acceptance. No completed validation record
supporting promotion to Concluído was identified for this card's thesis scope.

### Required evidence before Concluído

- [ ] Derive the configured base from the electrical model and document phase/line and RMS/peak conventions and units.
- [ ] Reconcile base_voltage = 100000.0 with the 138 kV line described in main.tex; record the justified value without assuming these quantities use the same convention.
- [ ] Independently check at least three LIS-to-CSV conversions and document the use of magnitude and the source maximum convention in the methodology.
- [ ] Record the validation date, reviewer, evidence links, thesis location,
  limitations, and justified acceptance decision.

### Related pending work

- [Definir o protocolo experimental](../pendente/01_protocolo_experimental.md)
- [Interpretar eletricamente os resultados](../pendente/06_interpretacao_eletrica.md)

## Como foi feito

Cada máximo é convertido pela expressão

\[
V_{pu} = \frac{|V|}{V_{base}}.
\]

O valor de `base_voltage` é informado no arquivo de configuração e validado
como número finito maior que zero. O módulo usa o valor absoluto para tratar
máximos positivos ou negativos pela magnitude da solicitação elétrica.

## Avaliação de validade

A fórmula implementada é válida. A validade física do resultado depende de
`base_voltage` representar a mesma convenção da grandeza extraída: tensão de
fase ou de linha, valor eficaz ou valor de pico. Os casos atuais usam
`100000.0`, mas o valor precisa ser justificado a partir do modelo elétrico e da
convenção empregada pelo ATP.

## Evidências e validação realizada

- Implementação: `src/services/preprocessing.py`.
- Validação da configuração: `src/services/config.py`.
- Testes numéricos: `tests/test_preprocessing.py` e `tests/test_config.py`.

## Verificação recomendada

Registrar no capítulo de metodologia a origem de `V_base` e conferir
manualmente ao menos três observações do `.lis` contra o CSV. A etapa estará
cientificamente consolidada quando a convenção de base estiver documentada e
os cálculos manuais coincidirem com o pipeline.

