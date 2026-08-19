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
    encoding: str
    base_voltage: float = Field(gt=0, allow_inf_nan=False)
    terminals: tuple[str, ...] = Field(min_length=1)
    phase_policy: Literal["A", "B", "C"]
    dbscan: DbscanConfig
    kmeans: KMeansConfig
    threshold: float = Field(allow_inf_nan=False)
    output_dir: Path
    overwrite: bool

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
        return self
