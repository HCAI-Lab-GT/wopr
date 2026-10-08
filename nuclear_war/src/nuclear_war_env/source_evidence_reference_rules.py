"""Shared source evidence reference validation rules."""

from __future__ import annotations

from typing import Any


def private_ref_errors(
    entry: dict[str, Any],
    line: str,
    id_field: str,
    item_id: str,
    reference_field: str,
) -> list[dict[str, str]]:
    if entry.get("evidence_kind") != "physical_copy":
        return []
    reference = entry.get(reference_field)
    if not isinstance(reference, str) or not reference.strip():
        return []
    if reference.startswith("private/"):
        return []
    payload = {
        "line": line,
        "field": reference_field,
        "error": "non_private_physical_copy_reference",
    }
    if item_id:
        payload[id_field] = item_id
    return [payload]


__all__ = ["private_ref_errors"]
