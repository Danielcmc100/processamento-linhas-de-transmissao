import re

from src.parser.models import (
    LisParseResult,
    MaximaData,
    SimulationRun,
    StatisticalSwitchConfig,
    SwitchEvent,
    VariableHeader,
)


class LisParseError(ValueError):
    """Report an unsupported or internally inconsistent statistical block."""


_RE_NENERG = re.compile(r"NENERG\s*=\s*(\d+)")

_RE_SWITCH_CONFIG = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s*$"
)

_RE_SIM_SPLIT = re.compile(
    r"Random switching times for simulation number\s+(\d+)\s*:"
)

_RE_DUMP_TIME = re.compile(
    r"Time\s*\[sec\]\s*=\s*([+-]?\d*\.?\d+(?:[Ee][+-]?\d+)?)"
)


def _parse_nenerg(text: str) -> int:
    """Extract NENERG (total simulations) from the text.

    Returns:
        Number of simulations, or 0 if not found.
    """
    match = _RE_NENERG.search(text)
    return int(match.group(1)) if match else 0


def _parse_switch_configs(
    text: str,
) -> list[StatisticalSwitchConfig]:
    """Extract statistical switch configuration table.

    Returns:
        List of switch configurations.
    """
    configs: list[StatisticalSwitchConfig] = []
    in_table = False
    found_data = False

    for line in text.splitlines():
        if "Entry" in line and "Switch" in line:
            in_table = True
            found_data = False
            continue

        if not in_table:
            continue

        stripped = line.strip()
        # Skip blank lines and non-data header rows (before we find data)
        if not stripped:
            if found_data:
                in_table = False
            continue

        match = _RE_SWITCH_CONFIG.match(line)
        if match:
            found_data = True
            configs.append(
                StatisticalSwitchConfig(
                    entry_number=int(match.group(1)),
                    switch_number=int(match.group(2)),
                    from_bus=match.group(3),
                    to_bus=match.group(4),
                    mean_time=float(match.group(5)),
                    std_dev=float(match.group(6)),
                    reference_switch=int(match.group(7)),
                )
            )
        elif found_data:
            # We already got data rows; stop on the first non-matching
            in_table = False
        # else: still in header rows, skip

    return configs


def _parse_variable_headers(
    text: str,
) -> list[VariableHeader]:
    """Extract variable/node column headers.

    Headers appear as paired lines between the
    statistical description and the first simulation.
    Each group (separated by blank lines) has a
    variable names line and an optional node names
    line. Groups have up to 10 columns each.

    Returns:
        Ordered list of variable headers.
    """
    headers: list[VariableHeader] = []

    first_sim = _RE_SIM_SPLIT.search(text)
    if not first_sim:
        return headers

    start_marker = "otherwise blank space"
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return headers

    # Move past the marker line
    newline_idx = text.find("\n", start_idx)
    if newline_idx == -1:
        return headers

    section = text[newline_idx : first_sim.start()]
    section = section.replace("\r", "")

    # Split into groups separated by blank lines
    raw_groups = re.split(r"\n[ \t]*\n", section)

    for group in raw_groups:
        lines = [ln for ln in group.splitlines() if ln.strip()]
        if not lines:
            continue

        var_tokens = lines[0].strip().split()

        node_tokens: list[str] = []
        if len(lines) > 1:
            node_str = lines[1].strip()
            ref_prefix = "Reference angle"
            if node_str.startswith(ref_prefix):
                node_str = node_str[len(ref_prefix) :].strip()
            node_tokens = node_str.split() if node_str else []

        for j, var in enumerate(var_tokens):
            node = node_tokens[j] if j < len(node_tokens) else ""
            headers.append(
                VariableHeader(
                    variable_name=var,
                    node_name=node,
                )
            )

    return headers


def _parse_simulation_runs(
    text: str,
    headers: list[VariableHeader],
) -> list[SimulationRun]:
    """Parse individual simulation run blocks.

    Returns:
        List of simulation runs with labeled maxima.
    """
    runs: list[SimulationRun] = []
    blocks = _RE_SIM_SPLIT.split(text)

    for i in range(1, len(blocks), 2):
        sim_num = int(blocks[i].strip())
        content = blocks[i + 1]

        has_dump = "==== Table dumping" in content
        table_dump_time: float | None = None

        if has_dump:
            dump_match = _RE_DUMP_TIME.search(content)
            if dump_match:
                table_dump_time = float(dump_match.group(1))

            sw_str = content.split("==== Table dumping")[0].strip()

            dump_parts = content.split("==== Table dumping", maxsplit=1)
            if "\n" not in dump_parts[1]:
                raise LisParseError(
                    f"simulation {sim_num} has no maxima table"
                )
            data_part = dump_parts[1].split("\n", maxsplit=1)[1]
        else:
            # Sim 2+: switching times on first lines,
            # then blank line, then peak value data
            lines = content.split("\n")
            sw_lines: list[str] = []
            data_start = 0
            found_sw = False

            for k, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    if found_sw:
                        data_start = k + 1
                        break
                    continue
                found_sw = True
                sw_lines.append(stripped)

            sw_str = " ".join(sw_lines)
            data_part = "\n".join(lines[data_start:])

        sw_tokens = sw_str.split()
        if len(sw_tokens) % 2 != 0:
            raise LisParseError(
                f"simulation {sim_num} has an incomplete switching-time pair"
            )

        try:
            switching_times: list[SwitchEvent] = [
                SwitchEvent(
                    switch_name=sw_tokens[j],
                    time=float(sw_tokens[j + 1]),
                )
                for j in range(0, len(sw_tokens), 2)
            ]
        except ValueError as error:
            raise LisParseError(
                f"simulation {sim_num} has a non-numeric switching time"
            ) from error

        if "Times of maxima :" not in data_part:
            raise LisParseError(
                f"simulation {sim_num} has no maxima-time table"
            )
        val_sec, time_sec = data_part.split("Times of maxima :", maxsplit=1)
        time_sec = re.split(r"\n[ \t]*\n", time_sec, maxsplit=1)[0]

        val_tokens = val_sec.split()
        time_tokens = time_sec.split()

        ref_angle: float | None = None
        if len(val_tokens) == len(time_tokens) + 1:
            try:
                ref_angle = float(val_tokens.pop(0))
            except ValueError as error:
                raise LisParseError(
                    f"simulation {sim_num} has a non-numeric reference angle"
                ) from error

        if len(val_tokens) != len(time_tokens):
            raise LisParseError(
                f"simulation {sim_num} has {len(val_tokens)} maxima values "
                f"but {len(time_tokens)} maxima times"
            )

        n = len(headers)
        if len(val_tokens) != n:
            raise LisParseError(
                f"simulation {sim_num} has {len(val_tokens)} maxima pairs "
                f"for {n} variable headers"
            )

        try:
            maxima_data: list[MaximaData] = [
                MaximaData(
                    variable_name=headers[idx].variable_name,
                    node_name=headers[idx].node_name,
                    value=float(val),
                    time=float(t),
                )
                for idx, (val, t) in enumerate(
                    zip(val_tokens, time_tokens, strict=True)
                )
            ]
        except ValueError as error:
            raise LisParseError(
                f"simulation {sim_num} has a non-numeric maximum or time"
            ) from error

        runs.append(
            SimulationRun(
                simulation_number=sim_num,
                table_dump_time=table_dump_time,
                reference_angle=ref_angle,
                switching_times=switching_times,
                maxima_data=maxima_data,
            )
        )

    return runs


def parse_statistical_data(
    text: str,
) -> LisParseResult:
    """Parse full .lis statistical simulation block.

    Returns:
        A model containing all parsed simulation data.
    """
    total_simulations = _parse_nenerg(text)
    if _RE_NENERG.search(text) is None:
        return LisParseResult()

    switch_configs = _parse_switch_configs(text)
    variable_headers = _parse_variable_headers(text)
    if total_simulations > 0 and not variable_headers:
        raise LisParseError(
            "statistical study does not contain supported variable headers"
        )

    runs = _parse_simulation_runs(text, variable_headers)
    if len(runs) != total_simulations:
        raise LisParseError(
            f"statistical study declares {total_simulations} simulations "
            f"but {len(runs)} runs were parsed"
        )

    run_ids = [run.simulation_number for run in runs]
    expected_ids = list(range(1, total_simulations + 1))
    if run_ids != expected_ids:
        raise LisParseError(
            "statistical study run identifiers are not contiguous from 1 "
            f"through {total_simulations}"
        )

    return LisParseResult(
        total_simulations=total_simulations,
        variable_headers=variable_headers,
        switch_configs=switch_configs,
        runs=runs,
    )
