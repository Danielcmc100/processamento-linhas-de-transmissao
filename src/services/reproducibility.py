"""Claim traceability and immutable reproducibility manifests."""

import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from PIL import Image, ImageSequence

SCHEMA_VERSION = "1.0.0"
GENERATOR_VERSION = "1.0.0"

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
_SUCCESS_STATUSES = {"accepted", "passed", "valid"}
_CLAIM_STATUSES = {"accepted", "blocked", "incomplete"}


def build_claim_evidence_row(
    *,
    requirement_id: str,
    claim_id: str,
    claim: str,
    code_paths: Sequence[str],
    test_paths: Sequence[str],
    data_paths: Sequence[str],
    output_artifacts: Sequence[str],
    figure_table_labels: Sequence[str],
    manuscript_sections: Sequence[str],
    status: str,
) -> dict[str, object]:
    """Build one complete claim-to-evidence traceability row.

    Returns:
        JSON-ready row linking one claim to every required evidence layer.

    Raises:
        ValueError: If an identifier, mapping layer, or status is invalid.
    """
    scalar_fields = {
        "requirement_id": requirement_id,
        "claim_id": claim_id,
        "claim": claim,
    }
    for name, value in scalar_fields.items():
        if not value.strip():
            raise ValueError(f"{name} must not be empty.")
    collections = {
        "code_paths": code_paths,
        "test_paths": test_paths,
        "data_paths": data_paths,
        "output_artifacts": output_artifacts,
        "figure_table_labels": figure_table_labels,
        "manuscript_sections": manuscript_sections,
    }
    normalized: dict[str, list[str]] = {}
    for name, values in collections.items():
        items = [value for value in values if value.strip()]
        if not items:
            raise ValueError(f"{name} must contain at least one value.")
        normalized[name] = items
    if status not in _CLAIM_STATUSES:
        options = ", ".join(sorted(_CLAIM_STATUSES))
        raise ValueError(f"status must be one of: {options}.")
    return {**scalar_fields, **normalized, "status": status}


def build_reproducibility_manifest(
    *,
    source_files: Mapping[str, Path],
    configuration: Mapping[str, Any],
    code_revision: str,
    dependencies: Mapping[str, str],
    commands: Sequence[str],
    output_files: Mapping[str, Path],
    generated_at_utc: str,
    validation_statuses: Mapping[str, str],
    claim_evidence: Sequence[Mapping[str, object]],
    nondeterministic_json_fields: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Build one deterministic package manifest with raw and semantic hashes.

    Runtime timestamp is recorded, but callers must explicitly declare any
    JSON fields excluded from artifact semantic hashes. Bitmap semantic hashes
    cover decoded dimensions, modes, frames, and pixels while excluding file
    metadata.

    Returns:
        JSON-ready provenance, traceability, status, and hash manifest.

    Raises:
        ValueError: If required provenance or exclusion declarations fail.
        FileNotFoundError: If a declared source or output does not exist.
    """
    exclusions = nondeterministic_json_fields or {}
    _validate_manifest_inputs(
        source_files=source_files,
        code_revision=code_revision,
        dependencies=dependencies,
        commands=commands,
        output_files=output_files,
        generated_at_utc=generated_at_utc,
        validation_statuses=validation_statuses,
        claim_evidence=claim_evidence,
        exclusions=exclusions,
    )
    configuration_bytes = _canonical_json_bytes(configuration)
    sources = [
        {
            "name": name,
            "path": str(path),
            "sha256": _file_sha256(path),
        }
        for name, path in sorted(source_files.items())
    ]
    outputs = [
        _output_record(
            name,
            path,
            tuple(exclusions.get(name, ())),
        )
        for name, path in sorted(output_files.items())
    ]
    claim_rows = [dict(row) for row in claim_evidence]
    all_gates_pass = all(
        status in _SUCCESS_STATUSES for status in validation_statuses.values()
    )
    all_claims_accepted = all(
        row.get("status") == "accepted" for row in claim_rows
    )
    package_status = (
        "complete" if all_gates_pass and all_claims_accepted else "incomplete"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at_utc": generated_at_utc,
        "package_status": package_status,
        "code_revision": code_revision,
        "dependencies": dict(sorted(dependencies.items())),
        "commands": list(commands),
        "configuration": {
            "value": dict(configuration),
            "sha256": sha256(configuration_bytes).hexdigest(),
        },
        "sources": sources,
        "outputs": outputs,
        "validation_statuses": dict(sorted(validation_statuses.items())),
        "claim_evidence": claim_rows,
        "semantic_hash_policy": {
            "json_exclusions": {
                name: sorted(fields)
                for name, fields in sorted(exclusions.items())
            },
            "image_metadata": "excluded",
        },
    }


def semantic_sha256(
    path: Path,
    *,
    json_exclusions: Sequence[str] = (),
) -> str:
    """Hash artifact semantics under an explicit deterministic policy.

    Returns:
        SHA-256 over canonical JSON, decoded image pixels, or raw bytes.

    Raises:
        ValueError: If a JSON exclusion path does not exist.
    """
    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open(encoding="utf-8") as source:
            value: Any = json.load(source)
        for field_path in json_exclusions:
            _remove_json_field(value, field_path)
        return sha256(_canonical_json_bytes(value)).hexdigest()
    if suffix in _IMAGE_SUFFIXES:
        return _image_semantic_sha256(path)
    if json_exclusions:
        raise ValueError("JSON exclusions are valid only for JSON artifacts.")
    return _file_sha256(path)


def artifacts_semantically_equal(
    first: Path,
    second: Path,
    *,
    json_exclusions: Sequence[str] = (),
) -> bool:
    """Return whether two artifacts have equal declared semantics."""
    if first.suffix.lower() != second.suffix.lower():
        return False
    return semantic_sha256(
        first,
        json_exclusions=json_exclusions,
    ) == semantic_sha256(second, json_exclusions=json_exclusions)


def validate_reproducibility_manifest(manifest: Mapping[str, object]) -> None:
    """Reject incompatible or incomplete reproducibility manifest schemas.

    Raises:
        ValueError: If schema version differs or required fields are absent.
    """
    actual = manifest.get("schema_version", "<missing>")
    if actual != SCHEMA_VERSION:
        message = (
            "Reproducibility schema mismatch: expected "
            f"{SCHEMA_VERSION}, got {actual}."
        )
        raise ValueError(message)
    required = {
        "generator_version",
        "generated_at_utc",
        "package_status",
        "code_revision",
        "dependencies",
        "commands",
        "configuration",
        "sources",
        "outputs",
        "validation_statuses",
        "claim_evidence",
        "semantic_hash_policy",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise ValueError(
            f"Reproducibility manifest fields missing: {', '.join(missing)}."
        )


def _output_record(
    name: str,
    path: Path,
    json_exclusions: tuple[str, ...],
) -> dict[str, object]:
    """Build one output record with byte and semantic hashes."""
    return {
        "name": name,
        "path": str(path),
        "sha256": _file_sha256(path),
        "semantic_sha256": semantic_sha256(
            path,
            json_exclusions=json_exclusions,
        ),
    }


def _validate_manifest_inputs(
    *,
    source_files: Mapping[str, Path],
    code_revision: str,
    dependencies: Mapping[str, str],
    commands: Sequence[str],
    output_files: Mapping[str, Path],
    generated_at_utc: str,
    validation_statuses: Mapping[str, str],
    claim_evidence: Sequence[Mapping[str, object]],
    exclusions: Mapping[str, Sequence[str]],
) -> None:
    """Validate required provenance before reading artifacts."""
    required_values = {
        "source_files": source_files,
        "code_revision": code_revision,
        "dependencies": dependencies,
        "commands": commands,
        "output_files": output_files,
        "validation_statuses": validation_statuses,
        "claim_evidence": claim_evidence,
    }
    for name, value in required_values.items():
        if not value:
            raise ValueError(f"{name} must not be empty.")
    try:
        parsed_time = datetime.fromisoformat(
            generated_at_utc.replace("Z", "+00:00")
        )
    except ValueError as error:
        message = "generated_at_utc must be an ISO-8601 timestamp."
        raise ValueError(message) from error
    if parsed_time.tzinfo is None:
        raise ValueError("generated_at_utc must include a timezone.")
    unknown_outputs = sorted(exclusions.keys() - output_files.keys())
    if unknown_outputs:
        names = ", ".join(unknown_outputs)
        raise ValueError(
            f"JSON exclusions reference unknown outputs: {names}."
        )
    for name, path in (*source_files.items(), *output_files.items()):
        if not path.is_file():
            raise FileNotFoundError(
                f"Declared artifact does not exist: {name}."
            )


def _canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON with stable ordering and no non-finite values."""
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _remove_json_field(value: Any, field_path: str) -> None:
    """Remove one exact dotted mapping path from a parsed JSON value."""
    parts = field_path.split(".")
    if not field_path or any(not part for part in parts):
        raise ValueError(f"Invalid JSON exclusion path: {field_path!r}.")
    current = value
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            raise ValueError(
                f"JSON exclusion path does not exist: {field_path}."
            )
        current = current[part]
    final = parts[-1]
    if not isinstance(current, dict) or final not in current:
        raise ValueError(f"JSON exclusion path does not exist: {field_path}.")
    del current[final]


def _image_semantic_sha256(path: Path) -> str:
    """Hash decoded bitmap content without container metadata."""
    digest = sha256()
    with Image.open(path) as image:
        for frame in ImageSequence.Iterator(image):
            converted = frame.convert("RGBA")
            header = f"{converted.width}x{converted.height}|RGBA|".encode()
            digest.update(header)
            digest.update(converted.tobytes())
    return digest.hexdigest()


def _file_sha256(path: Path) -> str:
    """Hash file bytes in bounded chunks."""
    digest = sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
