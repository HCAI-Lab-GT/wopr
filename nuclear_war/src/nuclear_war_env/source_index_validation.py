"""Source-index file validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .source_validation import SOURCE_INDEX_PATH, source_id_is_valid


@dataclass(frozen=True)
class SourceIndexValidation:
    ids: set[str]
    errors: list[dict[str, str]]


def validate_source_index(path: Path = SOURCE_INDEX_PATH) -> SourceIndexValidation:
    try:
        entries = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except FileNotFoundError:
        return SourceIndexValidation(
            ids=set(),
            errors=[{"path": str(path), "error": "missing"}],
        )
    except (json.JSONDecodeError, ValueError):
        return SourceIndexValidation(
            ids=set(),
            errors=[{"path": str(path), "error": "malformed_json"}],
        )
    if not isinstance(entries, list):
        return SourceIndexValidation(
            ids=set(),
            errors=[{"path": str(path), "error": "invalid_shape"}],
        )
    invalid_ids = _invalid_entry_ids(entries, path)
    duplicate_ids = _duplicate_entry_ids(entries, path)
    return SourceIndexValidation(
        ids={
            entry["id"]
            for entry in entries
            if isinstance(entry, dict) and source_id_is_valid(entry.get("id"))
        },
        errors=invalid_ids + duplicate_ids,
    )


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def _invalid_entry_ids(entries: list[object], path: Path) -> list[dict[str, str]]:
    invalid: list[dict[str, str]] = []
    for index, entry in enumerate(entries, 1):
        source_id = entry.get("id") if isinstance(entry, dict) else None
        if not source_id_is_valid(source_id):
            invalid.append(
                {
                    "path": str(path),
                    "error": "invalid_entry_id",
                    "line": str(index),
                }
            )
    return invalid


def _duplicate_entry_ids(entries: list[object], path: Path) -> list[dict[str, str]]:
    seen: dict[str, int] = {}
    duplicates: list[dict[str, str]] = []
    for index, entry in enumerate(entries, 1):
        source_id = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(source_id, str) or not source_id.strip():
            continue
        if source_id in seen:
            duplicates.append(
                {
                    "path": str(path),
                    "error": "duplicate_entry_id",
                    "source_id": source_id,
                    "first_line": str(seen[source_id]),
                    "duplicate_line": str(index),
                }
            )
        else:
            seen[source_id] = index
    return duplicates
