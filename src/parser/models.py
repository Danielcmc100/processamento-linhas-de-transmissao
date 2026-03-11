from pydantic import BaseModel, Field


class VariableHeader(BaseModel):
    """Column header mapping a variable to its node pair."""

    variable_name: str
    node_name: str


class StatisticalSwitchConfig(BaseModel):
    """Configuration of a statistical switch from the .lis file."""

    entry_number: int
    switch_number: int
    from_bus: str
    to_bus: str
    mean_time: float
    std_dev: float
    reference_switch: int


class SwitchEvent(BaseModel):
    """Switching time for a specific switch in a simulation."""

    switch_name: str
    time: float


class MaximaData(BaseModel):
    """Peak value and time of occurrence for a monitored variable."""

    variable_name: str
    node_name: str
    value: float
    time: float


class SimulationRun(BaseModel):
    """Data for a single statistical simulation run."""

    simulation_number: int
    table_dump_time: float | None = None
    reference_angle: float | None = None
    switching_times: list[SwitchEvent] = Field(default_factory=list)
    maxima_data: list[MaximaData] = Field(default_factory=list)


class LisParseResult(BaseModel):
    """Container for the full parsed .lis statistical data."""

    total_simulations: int = 0
    variable_headers: list[VariableHeader] = Field(default_factory=list)
    switch_configs: list[StatisticalSwitchConfig] = Field(default_factory=list)
    runs: list[SimulationRun] = Field(default_factory=list)
