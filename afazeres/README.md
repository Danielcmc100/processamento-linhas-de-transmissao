# TCC progress review

Assessment date: 2026-09-07. Workflow updated: 2026-09-11. Classification is based on the implementation in
`src/`, automated test definitions, saved experimental artifacts, and the
current text of [the thesis](../doc/main.tex).

## Status criteria

- **Concluído:** delivered and scientifically validated for its stated thesis
  scope, with traceable evidence, an explicit validation decision, and the
  corresponding method or result documented in the thesis.
- **Validando:** implementation, artifacts, or draft text already exist, but
  the evidence required for scientific acceptance is incomplete. This status
  includes items awaiting validation; it does not imply an experiment is running.
- **Pendente:** the planned deliverable or validation study has not yet been
  completed. Once produced, it must pass through validation before completion.

Passing software tests, generating a CSV, or compiling the thesis is evidence
of technical progress, but does not alone establish scientific acceptance.
For supporting tasks such as parsing and reporting, acceptance concerns data
fidelity and reproducibility within the declared scope; they do not need to
prove every downstream statistical hypothesis.

## Concluído

1. [Parser dos arquivos ATP](concluido/01_parser_arquivos_atp.md)
   ([Plane TCCKL-8](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-8))

2. [Estruturação das observações](concluido/02_estruturacao_observacoes.md)
   ([Plane TCCKL-9](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-9))

3. [Conversão das tensões para P.U.](concluido/03_conversao_para_pu.md)
   ([Plane TCCKL-10](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-10))

Accepted on 2026-09-11 with the ATP base of 112677 V;
see the [P.U. justification in the thesis](../doc/main.tex).

The parser was accepted again on 2026-09-10 after the CRPI repair and
source-fidelity audit. Historical decisions remain in its evidence record.

## Validando

The 9 items below require the recorded acceptance evidence. TCCKL-9 was
accepted again on 2026-09-10 after its separate SRPI/CRPI observation audit;
see the [validation report](../doc/observation_structure_validation_report.md).

1. [Validação e limpeza dos dados](validando/04_validacao_limpeza_dados.md)
   ([Plane TCCKL-11](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-11))
2. [Estatística descritiva e regra de três sigmas](validando/05_estatistica_tres_sigmas.md)
   ([Plane TCCKL-12](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-12))
3. [Ajuste Gaussiano e probabilidades de excedência](validando/06_ajuste_gaussiano_excedencia.md)
   ([Plane TCCKL-13](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-13))
4. [Implementação do DBSCAN e do K-Means](validando/07_implementacao_clusterizacao.md)
   ([Plane TCCKL-14](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-14))
5. [Comparação computacional dos indícios de anomalia](validando/08_comparacao_indicios_anomalia.md)
   ([Plane TCCKL-15](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-15))
6. [Artefatos e reprodutibilidade das execuções](validando/09_artefatos_reprodutibilidade.md)
   ([Plane TCCKL-16](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-16))
7. [Execuções por tamanho de amostra](validando/10_execucoes_tamanhos_amostra.md)
    ([Plane TCCKL-17](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-17))
8. [Qualidade e testes do software](validando/11_qualidade_testes_software.md)
    ([Plane TCCKL-18](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-18))
9. [Capítulos iniciais do TCC](validando/12_capitulos_iniciais_tcc.md)
    ([Plane TCCKL-19](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-19))

## Pendente

These eight deliverables remain pending. They describe the work needed to
validate the existing implementation and finish the thesis, rather than
additional copies of the implemented features.

1. [Definir o protocolo experimental](pendente/01_protocolo_experimental.md)
   ([Plane TCCKL-20](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-20))
2. [Analisar todas as fases e os cenários relevantes](pendente/02_fases_e_cenarios.md)
   ([Plane TCCKL-21](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-21))
3. [Validar a hipótese Gaussiana](pendente/03_validacao_hipotese_gaussiana.md)
   ([Plane TCCKL-22](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-22))
4. [Validar tecnicamente as anomalias](pendente/04_validacao_anomalias.md)
   ([Plane TCCKL-23](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-23))
5. [Comparar formalmente os métodos](pendente/05_comparacao_formal_metodos.md)
   ([Plane TCCKL-24](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-24))
6. [Interpretar eletricamente os resultados](pendente/06_interpretacao_eletrica.md)
   ([Plane TCCKL-25](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-25))
7. [Redigir os capítulos finais](pendente/07_capitulos_finais.md)
   ([Plane TCCKL-26](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-26))
8. [Realizar a revisão final do TCC](pendente/08_revisao_final_tcc.md)
   ([Plane TCCKL-27](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-27))

## Moving an item to Concluído

1. Meet the item-specific acceptance criteria and record the evaluated scope.
2. Link the input cases, configurations, code revision, validation procedure,
   expected outcomes or reference, actual results, and known limitations.
3. Record the validation date, reviewer, and justified acceptance decision.
   Include technical review where physical interpretation requires it.
4. Link the corresponding thesis section, table, or figure. Rejected hypotheses
   may also close an item when the decision and its consequences are documented;
   completion does not require a positive result.
5. Move the card from `validando/` to `concluido/` and update this index. Reopen
   validation if changes invalidate the recorded evidence or extend its scope.

Current totals: **3 Concluído, 9 Validando, 8 Pendente**. These are workflow
counts, not a percentage estimate of scientific completion.

## Dependency and priority tree

This tree follows the **blocked_by** relations recorded in Plane. A task can
appear in more than one branch because the workflow is a dependency graph, not
a strictly linear sequence.

Priority follows the Plane cards: **URGENT**, **HIGH**, **MEDIUM**, and **LOW**.

- Parser dos arquivos ATP
  ([local evidence](concluido/01_parser_arquivos_atp.md),
  [Plane TCCKL-8](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-8))
  **[MEDIUM]**
  - Estruturação das observações
    ([local evidence](concluido/02_estruturacao_observacoes.md),
    [Plane TCCKL-9](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-9))
    **[MEDIUM]**
    - Conversão das tensões para P.U.
      ([Plane TCCKL-10](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-10))
      **[HIGH]**
      - Validação e limpeza dos dados
        ([Plane TCCKL-11](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-11))
        **[MEDIUM]**
        - Estatística descritiva e regra de três sigmas
          ([Plane TCCKL-12](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-12))
          **[MEDIUM]**
          - Ajuste Gaussiano e probabilidades de excedência
            ([Plane TCCKL-13](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-13))
            **[MEDIUM]**
            - Validar a hipótese Gaussiana
              ([Plane TCCKL-22](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-22))
              **[HIGH]**
        - Implementação do DBSCAN e do K-Means
          ([Plane TCCKL-14](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-14))
          **[MEDIUM]**
          - Comparação computacional dos indícios de anomalia
            ([Plane TCCKL-15](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-15))
            **[HIGH]**

- Definir o protocolo experimental
  ([Plane TCCKL-20](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-20))
  **[URGENT]**
  - Analisar todas as fases e os cenários relevantes
    ([Plane TCCKL-21](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-21))
    **[HIGH]**
    - Execuções por tamanho de amostra
      ([Plane TCCKL-17](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-17))
      **[MEDIUM]**
      - Validar tecnicamente as anomalias
        ([Plane TCCKL-23](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-23))
        **[URGENT]**
        - Comparar formalmente os métodos
          ([Plane TCCKL-24](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-24))
          **[HIGH]**
          - Interpretar eletricamente os resultados
            ([Plane TCCKL-25](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-25))
            **[HIGH]**
            - Capítulos iniciais do TCC
              ([Plane TCCKL-19](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-19))
              **[MEDIUM]**
              - Redigir os capítulos finais
                ([Plane TCCKL-26](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-26))
                **[MEDIUM]**
                - Realizar a revisão final do TCC
                  ([Plane TCCKL-27](https://app.plane.so/tcc-kleber-viana/browse/TCCKL-27))
                  **[LOW]**

Additional cross-dependencies from Plane:

- **Definir o protocolo experimental** also blocks statistics, Gaussian
  fitting, clustering, sample-size runs, anomaly validation, and software
  quality.
- **Validacao e limpeza dos dados** also blocks sample-size runs and clustering.
- **Estatistica descritiva e regra de tres sigmas** also blocks the
  computational anomaly comparison.
- **Ajuste Gaussiano e probabilidades de excedencia** and **Execucoes por
  tamanho de amostra** both block **Validar a hipotese Gaussiana**.
- **Comparacao computacional dos indicios de anomalia** also blocks formal
  method comparison and technical anomaly validation.
- **Artefatos e reprodutibilidade das execucoes** depends on the protocol,
  scenarios, and sample-size runs, and blocks the final chapters.
- **Qualidade e testes do software** depends on the protocol and parser, and
  blocks the final chapters.
- **Interpretar eletricamente os resultados** and **Capitulos iniciais do TCC**
  are both prerequisites for the final chapters.

See the [evidence review](../doc/scientific_validation_status_review.md) for
repository findings and the rationale for this reclassification.
