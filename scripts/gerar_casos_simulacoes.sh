#!/usr/bin/env bash
# Gera pastas de casos (100/200/1000/10000-simulacoes) a partir de 50-simulacoes.
# Copia apenas .xml e .atp (os demais: .lis .pl4 .dat sao gerados a partir do .atp
# ao rodar a simulacao, nao devem ser copiados). Nao copia a pasta resultados.
# Ajusta input.json de cada pasta nova.

set -euo pipefail

BASE_DIR="input_files/casos"
SRC="50-simulacoes"
TARGETS=(100 200 1000 10000)

cd "$(dirname "$0")/.."

for N in "${TARGETS[@]}"; do
    DEST="${N}-simulacoes"
    SRC_CASOS="${BASE_DIR}/${SRC}/casos"
    DEST_CASOS="${BASE_DIR}/${DEST}/casos"

    echo "==> Criando ${BASE_DIR}/${DEST}"
    mkdir -p "${DEST_CASOS}"

    # copia so .xml e .atp, preservando estrutura de diretorios
    (cd "${SRC_CASOS}" && find . -type f \( -name '*.xml' -o -name '*.atp' \)) \
        | while read -r f; do
            mkdir -p "${DEST_CASOS}/$(dirname "$f")"
            cp "${SRC_CASOS}/${f}" "${DEST_CASOS}/${f}"
        done

    # ajusta input.json
    sed "s#${BASE_DIR}/${SRC}#${BASE_DIR}/${DEST}#g" \
        "${BASE_DIR}/${SRC}/input.json" > "${BASE_DIR}/${DEST}/input.json"

    # ajusta NENERG (numero de simulacoes estatisticas) no cartao MISCELL,
    # linha 11 do .atp, campo de 8 colunas, alinhado a direita
    NOVO_CAMPO=$(printf '%8d' "$N")
    find "${DEST_CASOS}" -name '*.atp' | while read -r atp; do
        sed -i "11s/.\{8\}\$/${NOVO_CAMPO}/" "$atp"
    done

    echo "    $(find "${DEST_CASOS}" -type f | wc -l) arquivos copiados"
done

echo "Concluido."
