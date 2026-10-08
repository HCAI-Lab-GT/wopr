"""Card-effect source evidence manifest validation."""

from __future__ import annotations

import json
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

from .card_effect_evidence_rules import (
    evidence_entry_errors,
    evidence_entry_verified,
    reject_json_constant,
)

_RESEARCH_ROOT = Path(__file__).resolve().parents[2] / "research"
CARD_EFFECT_EVIDENCE_PATH = (
    _RESEARCH_ROOT / "source_evidence" / ("card_effect_evidence.jsonl")
)


@dataclass(frozen=True)
class CardEffectEvidenceValidation:
    path: Path
    status: str
    record_count: int
    verified_record_count: int
    errors: list[dict[str, str]]

    @property
    def present(self) -> bool:
        return self.status == "present"

    def to_payload(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "status": self.status,
            "record_count": self.record_count,
            "verified_record_count": self.verified_record_count,
            "errors": self.errors,
        }


def validate_card_effect_evidence_manifest(
    path: Path = CARD_EFFECT_EVIDENCE_PATH,
    known_card_ids: Collection[str] | None = None,
) -> CardEffectEvidenceValidation:
    if not path.exists():
        return CardEffectEvidenceValidation(path, "missing", 0, 0, [])
    known_ids = set(known_card_ids) if known_card_ids is not None else None
    records = 0
    verified = 0
    errors: list[dict[str, str]] = []
    seen: dict[str, int] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
        if not line:
            continue
        try:
            entry = json.loads(line, parse_constant=reject_json_constant)
        except (json.JSONDecodeError, ValueError):
            errors.append({"line": str(line_number), "error": "malformed_json"})
            continue
        if not isinstance(entry, dict):
            errors.append({"line": str(line_number), "error": "invalid_shape"})
            continue
        records += 1
        line = str(line_number)
        errors.extend(evidence_entry_errors(entry, line_number, seen))
        errors.extend(_known_card_id_errors(entry, line, known_ids))
        if evidence_entry_verified(entry):
            verified += 1
    return CardEffectEvidenceValidation(path, "present", records, verified, errors)


def _known_card_id_errors(
    entry: dict[str, object],
    line: str,
    known_ids: set[str] | None,
) -> list[dict[str, str]]:
    if known_ids is None:
        return []
    card_id = entry.get("card_id")
    if not isinstance(card_id, str) or not card_id:
        return []
    if card_id in known_ids:
        return []
    return [
        {
            "line": line,
            "card_id": card_id,
            "field": "card_id",
            "error": "unknown_card_id",
        }
    ]


__all__ = [
    "CARD_EFFECT_EVIDENCE_PATH",
    "CardEffectEvidenceValidation",
    "validate_card_effect_evidence_manifest",
]
