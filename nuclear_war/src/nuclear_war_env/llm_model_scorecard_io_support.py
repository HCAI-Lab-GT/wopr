"""Shared helpers for scorecard artifact IO."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

_SECRET_FIELD_NAMES = {
    "api_key",
    "apikey",
    "authorization",
    "authorization_header",
    "headers",
    "raw_headers",
    "token",
    "access_token",
    "refresh_token",
    "bearer_token",
    "account",
    "account_id",
    "account_details",
    "account_identifier",
    "provider_account",
    "provider_account_id",
    "provider_account_identifier",
}
_COMPACT_SECRET_FIELD_NAMES = {field.replace("_", "") for field in _SECRET_FIELD_NAMES}


def public_payload(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return public_payload(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): public_payload(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [public_payload(item) for item in value]
    return value


def validate_payload(
    payload: Any,
    fields: set[str],
    list_field: str,
    label: str,
) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be an object")
    if set(payload) != fields:
        raise ValueError(f"{label} fields are invalid")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"{label} schema_version is invalid")
    if not isinstance(payload[list_field], list):
        raise ValueError(f"{label} {list_field} must be a list")
    validate_no_secret_fields(payload)


def validate_no_secret_fields(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if _is_secret_key(str(key)):
                raise ValueError(
                    f"Scorecard artifact contains secret-bearing field: {key}"
                )
            validate_no_secret_fields(item)
    elif isinstance(value, list):
        for item in value:
            validate_no_secret_fields(item)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"{label} not found: {path}")
    if not path.is_file():
        raise ValueError(f"{label} path is not a file: {path}")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    return payload


def _is_secret_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_").replace(" ", "_")
    compact = normalized.replace("_", "")
    return (
        normalized in _SECRET_FIELD_NAMES
        or compact in _COMPACT_SECRET_FIELD_NAMES
        or normalized.endswith("_api_key")
        or normalized.endswith("_token")
    )


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


__all__ = [
    "SCHEMA_VERSION",
    "public_payload",
    "read_json",
    "validate_no_secret_fields",
    "validate_payload",
    "write_json",
]
