"""Patito schema models for the Polars DataFrames used across services."""

from patito import Field, Model
from polars import Int32, Int64


class MaximaObservation(Model):
    """One phase-to-ground voltage maximum, normalized to P.U."""

    source_file: str
    simulation: int = Field(dtype=Int32)
    terminal: str
    phase: str
    value_pu: float
    time: float
    source_value: float
    scenario: str
    sample_size: int = Field(dtype=Int64)
    source_lineage: str
    base_voltage: float
    event_definition: str


class SwitchingTimeObservation(Model):
    """One simulated breaker switching event and its configured Gaussian."""

    source_file: str
    simulation: int = Field(dtype=Int32)
    switch_number: int = Field(dtype=Int32)
    opening_time: float
    mean_time: float | None
    std_dev: float | None


class SigmaSummaryRow(Model):
    """One sigma-level row (1σ to 6σ) with threshold and exceedance."""

    sigma: int = Field(dtype=Int64)
    threshold_pu: float
    exceedance_prob: float


class StatisticalSummaryRow(Model):
    """One terminal/phase exceedance summary row."""

    terminal: str
    phase: str
    n_total: int = Field(dtype=Int64)
    n_valid: int = Field(dtype=Int64)
    mean: float | None
    std: float | None
    sigma_3_threshold: float | None
    empirical_exceedance: float | None
    gaussian_exceedance: float | None
    validation_status: str
