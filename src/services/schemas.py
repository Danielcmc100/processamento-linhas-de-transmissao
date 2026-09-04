"""Patito schema models for the Polars DataFrames used across services."""

import patito as pt
import polars as pl


class MaximaObservation(pt.Model):
    """One phase-to-ground voltage maximum, normalized to P.U."""

    source_file: str
    simulation: int = pt.Field(dtype=pl.Int32)
    terminal: str
    phase: str
    value_pu: float
    time: float


class SwitchingTimeObservation(pt.Model):
    """One simulated breaker switching event and its configured Gaussian."""

    source_file: str
    simulation: int = pt.Field(dtype=pl.Int32)
    switch_number: int = pt.Field(dtype=pl.Int32)
    opening_time: float
    mean_time: float | None
    std_dev: float | None


class SigmaSummaryRow(pt.Model):
    """One sigma-level row (1σ to 6σ) with threshold and exceedance."""

    sigma: int = pt.Field(dtype=pl.Int64)
    threshold_pu: float
    exceedance_prob: float


class StatisticalSummaryRow(pt.Model):
    """One terminal/phase exceedance summary row."""

    terminal: str
    phase: str
    n_total: int = pt.Field(dtype=pl.Int64)
    n_valid: int = pt.Field(dtype=pl.Int64)
    mean: float | None
    std: float | None
    sigma_3_threshold: float | None
    empirical_exceedance: float | None
    gaussian_exceedance: float | None
    validation_status: str
