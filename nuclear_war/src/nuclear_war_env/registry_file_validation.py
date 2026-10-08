"""Registry JSONL shape validation."""

from __future__ import annotations

import json
from pathlib import Path

from .cards_registry import CardType


def registry_file_issues(path: Path) -> dict[str, list[dict[str, object]]]:
    seen: dict[str, int] = {}
    malformed: list[dict[str, object]] = []
    invalid_ids: list[dict[str, object]] = []
    invalid_types: list[dict[str, object]] = []
    duplicates: list[dict[str, object]] = []
    valid_types = {card_type.value for card_type in CardType}
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
        if not line:
            continue
        try:
            entry = json.loads(line, parse_constant=_reject_json_constant)
        except (json.JSONDecodeError, ValueError):
            malformed.append({"line": line_number})
            continue
        card_id = entry.get("id") if isinstance(entry, dict) else None
        card_type = entry.get("type") if isinstance(entry, dict) else None
        if not isinstance(card_id, str) or not card_id.strip():
            invalid_ids.append({"line": line_number, "id": card_id})
        elif card_id in seen:
            duplicates.append(
                {
                    "card_id": card_id,
                    "first_line": seen[card_id],
                    "duplicate_line": line_number,
                }
            )
        else:
            seen[card_id] = line_number
        if card_type not in valid_types:
            invalid_types.append(
                {"line": line_number, "card_id": card_id, "type": card_type}
            )
    return {
        "malformed_registry_lines": malformed,
        "invalid_card_ids": invalid_ids,
        "invalid_card_types": invalid_types,
        "duplicate_card_ids": duplicates,
    }


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")
