"""Expansion composition evidence entry validation rules."""

from __future__ import annotations

from collections.abc import Collection
from typing import Any

from .source_evidence_reference_rules import private_ref_errors as ref_err

PUBLIC_SAFE_REQUIRED_FIELDS = (
    "registry_id",
    "card_name",
    "expansion_set",
    "count_in_deck",
    "evidence_kind",
    "source_reference",
    "verification_status",
    "verified_by_second_pass",
)
RESTRICTED_FIELDS = {
    "exact_front_text",
    "exact_text",
    "official_text",
    "unofficial_text",
}
VALID_EVIDENCE_KINDS = {"physical_copy", "publisher_authorized_source"}
VALID_VERIFICATION_STATUSES = {"draft", "second_pass_verified", "transcribed"}


def evidence_entry_errors(
    entry: dict[str, Any],
    line_number: int,
    seen: dict[str, int],
    known_registry_ids: Collection[str],
) -> list[dict[str, str]]:
    registry_id = _registry_id(entry)
    errors: list[dict[str, str]] = []
    line = str(line_number)
    for field in PUBLIC_SAFE_REQUIRED_FIELDS:
        if _missing_required_value(entry, field):
            errors.append(_field_error(line, registry_id, field, "missing_required"))
    if registry_id:
        errors.extend(_registry_id_errors(line, registry_id, seen, known_registry_ids))
    if not _valid_count(entry.get("count_in_deck")):
        errors.append(_field_error(line, registry_id, "count_in_deck", "invalid_count"))
    if entry.get("evidence_kind") not in VALID_EVIDENCE_KINDS:
        errors.append(_field_error(line, registry_id, "evidence_kind", "invalid_value"))
    errors.extend(ref_err(entry, line, "registry_id", registry_id, "source_reference"))
    if entry.get("verification_status") not in VALID_VERIFICATION_STATUSES:
        errors.append(
            _field_error(line, registry_id, "verification_status", "invalid_value")
        )
    if (
        entry.get("verification_status") == "second_pass_verified"
        and entry.get("verified_by_second_pass") is not True
    ):
        errors.append(
            _field_error(
                line,
                registry_id,
                "verified_by_second_pass",
                "second_pass_required",
            )
        )
    for field in _restricted_paths(entry):
        errors.append(_field_error(line, registry_id, field, "restricted_field"))
    return errors


def evidence_entry_verified(entry: dict[str, Any]) -> bool:
    return (
        entry.get("verification_status") == "second_pass_verified"
        and entry.get("verified_by_second_pass") is True
    )


def reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def _registry_id_errors(
    line: str,
    registry_id: str,
    seen: dict[str, int],
    known_registry_ids: Collection[str],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    first_line = seen.get(registry_id)
    if first_line is not None:
        errors.append(
            {
                "line": line,
                "registry_id": registry_id,
                "error": "duplicate_registry_id",
                "first_line": str(first_line),
            }
        )
    else:
        seen[registry_id] = int(line)
    if registry_id not in known_registry_ids:
        error = _field_error(line, registry_id, "registry_id", "unknown_registry_id")
        errors.append(error)
    return errors


def _missing_required_value(entry: dict[str, Any], field: str) -> bool:
    if field not in entry:
        return True
    value = entry[field]
    if field == "verified_by_second_pass":
        return not isinstance(value, bool)
    if field == "count_in_deck":
        return value is None
    return not isinstance(value, str) or not value.strip()


def _valid_count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _registry_id(entry: dict[str, Any]) -> str:
    value = entry.get("registry_id")
    return value if isinstance(value, str) else ""


def _field_error(line: str, registry_id: str, field: str, error: str) -> dict[str, str]:
    payload = {"line": line}
    if registry_id:
        payload["registry_id"] = registry_id
    payload["field"] = field
    payload["error"] = error
    return payload


def _restricted_paths(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        matches: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in RESTRICTED_FIELDS:
                matches.append(path)
            matches.extend(_restricted_paths(item, path))
        return matches
    if isinstance(value, list):
        matches = []
        for index, item in enumerate(value):
            path = f"{prefix}.{index}" if prefix else str(index)
            matches.extend(_restricted_paths(item, path))
        return matches
    return []


__all__ = ["evidence_entry_errors", "evidence_entry_verified", "reject_json_constant"]
