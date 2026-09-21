"""Validated configuration models for reproducible ATP analysis."""

from codecs import lookup
from pathlib import Path
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    field_validator,
    model_validator,
)


class DbscanConfig(BaseModel):
    """Validated DBSCAN parameters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    eps: float = Field(gt=0, allow_inf_nan=False)
    min_samples: int = Field(ge=1)


class KMeansConfig(BaseModel):
    """Validated deterministic K-Means parameters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    n_clusters: int = Field(ge=1)
    random_state: int


class AnalysisConfig(BaseModel):
    """Validated inputs and parameters for one ATP analysis run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    input_path: DirectoryPath
    schema_version: Literal["1.0.0"]
    generator_version: str
    encoding: str
    base_voltage: float = Field(gt=0, allow_inf_nan=False)
    scenario: Literal["SRPI", "CRPI"]
    sample_size: int = Field(gt=0)
    source_lineage: str
    event_definition: str
    terminals: tuple[str, ...] = Field(min_length=1)
    phase_policy: Literal["A", "B", "C"]
    dbscan: DbscanConfig
    kmeans: KMeansConfig
    threshold: float = Field(allow_inf_nan=False)
    output_dir: Path
    overwrite: bool
    grouping_policy: tuple[str, ...] = (
        "scenario",
        "source_lineage",
        "terminal",
        "phase",
    )
    mad_threshold: float = Field(default=3.5, allow_inf_nan=False)
    confidence_level: float = Field(default=0.95, allow_inf_nan=False)
    adequacy_significance_level: float = Field(
        default=0.05,
        allow_inf_nan=False,
    )
    kmeans_threshold_percentile: float = Field(
        default=99.0,
        allow_inf_nan=False,
    )
    dbscan_threshold_percentile: float = Field(
        default=95.0,
        allow_inf_nan=False,
    )

    @field_validator(
        "generator_version",
        "source_lineage",
        "event_definition",
    )
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        """Require non-blank provenance and scientific-policy text."""
        if not value.strip():
            raise ValueError("Configuration text fields must not be blank.")
        return value

    @field_validator("base_voltage")
    @classmethod
    def validate_base_voltage(cls, value: float) -> float:
        """Require accepted ATP P.U. base for comparable evidence."""
        if value != 112_677.0:
            raise ValueError("base_voltage must equal accepted 112677 V.")
        return value

    @field_validator("grouping_policy")
    @classmethod
    def validate_grouping_policy(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        """Freeze comparable anomaly groups for final evidence."""
        expected = (
            "scenario",
            "source_lineage",
            "terminal",
            "phase",
        )
        if value != expected:
            raise ValueError(
                "grouping_policy must be scenario, source_lineage, "
                "terminal, phase."
            )
        return value

    @field_validator("encoding")
    @classmethod
    def validate_encoding(cls, value: str) -> str:
        """Require an encoding recognized by the Python runtime.

        Raises:
            ValueError: If the encoding is unknown.
        """
        try:
            lookup(value)
        except LookupError as error:
            message = f"Unknown encoding: {value}."
            raise ValueError(message) from error
        return value

    @field_validator("terminals")
    @classmethod
    def validate_terminals(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        """Require distinct, non-blank terminal names.

        Raises:
            ValueError: If a terminal is blank or repeated.
        """
        if any(not terminal.strip() for terminal in value):
            message = "Terminal names must not be blank."
            raise ValueError(message)
        if len(set(value)) != len(value):
            message = "Terminal names must be unique."
            raise ValueError(message)
        return value

    @model_validator(mode="after")
    def validate_output_path(self) -> Self:
        """Reject output files and input/output directory collisions.

        Raises:
            ValueError: If the output path is unsafe for result artifacts.
        """
        if self.output_dir.exists() and not self.output_dir.is_dir():
            message = "Output path must be a directory."
            raise ValueError(message)
        if self.input_path.resolve() == self.output_dir.resolve():
            message = "Input and output directories must be different."
            raise ValueError(message)
        frozen_policies = {
            "mad_threshold": (self.mad_threshold, 3.5),
            "confidence_level": (self.confidence_level, 0.95),
            "adequacy_significance_level": (
                self.adequacy_significance_level,
                0.05,
            ),
            "kmeans_threshold_percentile": (
                self.kmeans_threshold_percentile,
                99.0,
            ),
            "dbscan_threshold_percentile": (
                self.dbscan_threshold_percentile,
                95.0,
            ),
        }
        for name, (actual, expected) in frozen_policies.items():
            if actual != expected:
                raise ValueError(
                    f"{name} is frozen at {expected:g} for schema 1.0.0."
                )
        return self
