"""Live source-evidence manifest promotion checks."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .card_effect_evidence_rules import (
    evidence_entry_verified as card_effect_entry_verified,
)
from .card_effect_evidence_rules import (
    reject_json_constant as reject_card_json_constant,
)
from .expansion_composition_evidence_rules import (
    evidence_entry_verified as expansion_entry_verified,
)
from .expansion_composition_evidence_rules import (
    reject_json_constant as reject_expansion_json_constant,
)

PROMOTION_ERROR = "live_manifest_requires_second_pass_verified"


def card_effect_promotion_errors(path: Path) -> list[dict[str, str]]:
    return _promotion_errors(
        path,
        "card_id",
        card_effect_entry_verified,
        reject_card_json_constant,
    )


def expansion_composition_promotion_errors(path: Path) -> list[dict[str, str]]:
    return _promotion_errors(
        path,
        "registry_id",
        expansion_entry_verified,
        reject_expansion_json_constant,
    )


def _promotion_errors(
    path: Path,
    id_field: str,
    entry_verified: Callable[[dict[str, Any]], bool],
    reject_json_constant: Callable[[str], None],
) -> list[dict[str, str]]:
    if not path.exists():
        return []
    errors: list[dict[str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
        if not line:
            continue
        try:
            entry = json.loads(line, parse_constant=reject_json_constant)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(entry, dict) or entry_verified(entry):
            continue
        errors.append(_promotion_error(entry, str(line_number), id_field))
    return errors


def _promotion_error(
    entry: dict[str, Any],
    line: str,
    id_field: str,
) -> dict[str, str]:
    payload = {
        "line": line,
        "field": "verification_status",
        "error": PROMOTION_ERROR,
    }
    identifier = entry.get(id_field)
    if isinstance(identifier, str) and identifier:
        payload[id_field] = identifier
    return payload


__all__ = [
    "PROMOTION_ERROR",
    "card_effect_promotion_errors",
    "expansion_composition_promotion_errors",
]
