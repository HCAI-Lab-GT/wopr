"""Card-effect evidence entry validation rules."""

from __future__ import annotations

from typing import Any

from .source_evidence_reference_rules import private_ref_errors as ref_err

PUBLIC_SAFE_REQUIRED_FIELDS = (
    "card_id",
    "card_name",
    "card_type",
    "count",
    "evidence_kind",
    "effect_summary",
    "source_photo_or_file",
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
) -> list[dict[str, str]]:
    card_id = _card_id(entry)
    errors: list[dict[str, str]] = []
    line = str(line_number)
    for field in PUBLIC_SAFE_REQUIRED_FIELDS:
        if _missing_required_value(entry, field):
            errors.append(_field_error(line, card_id, field, "missing_required"))
    if card_id:
        first_line = seen.get(card_id)
        if first_line is not None:
            errors.append(
                {
                    "line": line,
                    "card_id": card_id,
                    "error": "duplicate_card_id",
                    "first_line": str(first_line),
                }
            )
        else:
            seen[card_id] = line_number
    if not _valid_count(entry.get("count")):
        errors.append(_field_error(line, card_id, "count", "invalid_count"))
    if entry.get("evidence_kind") not in VALID_EVIDENCE_KINDS:
        errors.append(_field_error(line, card_id, "evidence_kind", "invalid_value"))
    errors.extend(ref_err(entry, line, "card_id", card_id, "source_photo_or_file"))
    if entry.get("verification_status") not in VALID_VERIFICATION_STATUSES:
        errors.append(
            _field_error(line, card_id, "verification_status", "invalid_value")
        )
    if (
        entry.get("verification_status") == "second_pass_verified"
        and entry.get("verified_by_second_pass") is not True
    ):
        errors.append(
            _field_error(
                line,
                card_id,
                "verified_by_second_pass",
                "second_pass_required",
            )
        )
    for field in _restricted_paths(entry):
        errors.append(_field_error(line, card_id, field, "restricted_field"))
    return errors


def evidence_entry_verified(entry: dict[str, Any]) -> bool:
    return (
        entry.get("verification_status") == "second_pass_verified"
        and entry.get("verified_by_second_pass") is True
    )


def reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def _missing_required_value(entry: dict[str, Any], field: str) -> bool:
    if field not in entry:
        return True
    value = entry[field]
    if field == "verified_by_second_pass":
        return not isinstance(value, bool)
    if field == "count":
        return value is None
    return not isinstance(value, str) or not value.strip()


def _valid_count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _card_id(entry: dict[str, Any]) -> str:
    value = entry.get("card_id")
    return value if isinstance(value, str) else ""


def _field_error(
    line: str,
    card_id: str,
    field: str,
    error: str,
) -> dict[str, str]:
    payload = {"line": line}
    if card_id:
        payload["card_id"] = card_id
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


__all__ = [
    "evidence_entry_errors",
    "evidence_entry_verified",
    "reject_json_constant",
]
