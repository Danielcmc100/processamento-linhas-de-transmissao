from collections import defaultdict
from enum import StrEnum
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import polars as pl
from polars import DataFrame

from src.models import VariableHeader
from src.parser import parse_statistical_data


class Terminal(StrEnum):
    T_MAN = "T_MAN"
    TOPO = "T_OPO"
    MIDLE = "1_2LT"
    ONE_QUARTER = "1_4LT"
    TRE_QUARTER = "3_4LT"


ISO_8859_1 = "iso-8859-1"

BASES = {
    Terminal.T_MAN: 408248,
    Terminal.TOPO: 408248,
    Terminal.MIDLE: 408248,
}

DISTANCES: dict[Terminal, float] = {
    Terminal.T_MAN: 0,
    Terminal.TOPO: 1,
    Terminal.MIDLE: 1 / 2,
    Terminal.ONE_QUARTER: 1 / 4,
    Terminal.TRE_QUARTER: 3 / 4,
}


def phase_ground_filter_function(header: VariableHeader) -> bool:
    return any(a in header.variable_name for a in Terminal) and header.node_name == ""


terminais: defaultdict[Terminal, list[Any]] = defaultdict(list)


direcotory = Path(
    "/home/daniel/Documentos/Trabalho/pos/INOCENCIO/enviados/ELT_INOCENSIO_QUEIMADOS/ELT"
)

fig, ax = plt.subplots(figsize=(10, 6))
labeled: set[Terminal] = set()
for lis_file, _ in zip(direcotory.rglob("*.lis"), range(2)):
    text = lis_file.read_text(encoding=ISO_8859_1)
    result = parse_statistical_data(text=text)

    phase_ground_filter = tuple(
        phase_ground_filter_function(header=header)
        for header in result.variable_headers
    )

    a = []

    for run in result.runs:
        maxima_data = run.maxima_data
        c = [maxima for maxima, bool in zip(maxima_data, phase_ground_filter) if bool]

        # print(str(c) + "\n")

        for data in c:
            name = data.variable_name[:-1]
            try:
                terminal = Terminal(name)
            except:
                message = f"{name} is not valid"
                raise ValueError(message)
            terminais[terminal].append(data)

    for terminal in Terminal:
        if terminal not in terminais:
            continue
        df = DataFrame(terminais[terminal])
        df: DataFrame = df.with_columns(pl.col("value").abs() / BASES[terminal])

        distancia = DISTANCES[terminal]
        values = df["value"].to_list()

        label = f"{terminal.value} ({distancia})" if terminal not in labeled else None
        labeled.add(terminal)
        _ = ax.hist(
            values,
            bins=30,
            label=label,
            alpha=0.6,
            edgecolor="black",
            linewidth=0.5,
        )


ax.set_xlabel("Tensão (p.u.)")
ax.set_ylabel("Frequência")
ax.set_title("Distribuição de Sobretensões por Terminal")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)
fig.tight_layout()
plt.show()


def teste() -> None:
    """Run the parser and print verification info."""
    text = LIS_PATH.read_text()
    result = parse_statistical_data(text=text)

    print(f"NENERG: {result.total_simulations}")
    print(f"Runs parsed: {len(result.runs)}")
    print(f"Variable headers: {len(result.variable_headers)}")
    print(f"Switch configs: {len(result.switch_configs)}")

    if result.switch_configs:
        print("\n--- Switch Configs ---")
        for sc in result.switch_configs:
            print(
                f"  #{sc.entry_number}: "
                + f"sw={sc.switch_number} "
                + f"{sc.from_bus}->{sc.to_bus} "
                + f"mean={sc.mean_time} "
                + f"std={sc.std_dev}"
            )

    if result.variable_headers:
        print("\n--- First 10 Variable Headers ---")
        for vh in result.variable_headers[:10]:
            print(f"  {vh.variable_name} @ {vh.node_name}")

    if result.runs:
        run1 = result.runs[0]
        print(f"\n--- Simulation {run1.simulation_number} ---")
        print(f"  ref_angle: {run1.reference_angle}")
        print(f"  dump_time: {run1.table_dump_time}")
        print("  switching_times:")
        for sw in run1.switching_times:
            print(f"    {sw.switch_name}: {sw.time}")
        print(f"  maxima_data count: {len(run1.maxima_data)}")
        if run1.maxima_data:
            print("  first 5 maxima:")
            for m in run1.maxima_data[:5]:
                print(f"    {m.variable_name}@{m.node_name}: val={m.value} t={m.time}")


if __name__ == "__main__":
    ...
    # teste()
