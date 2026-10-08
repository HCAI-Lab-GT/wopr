"""Expansion composition source evidence manifest validation."""

from __future__ import annotations

import json
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

from .expansion_composition_evidence_rules import (
    evidence_entry_errors,
    evidence_entry_verified,
    reject_json_constant,
)
from .expansions import catalog_registry_ids

_RESEARCH_ROOT = Path(__file__).resolve().parents[2] / "research"
EXPANSION_COMPOSITION_EVIDENCE_PATH = (
    _RESEARCH_ROOT / "source_evidence" / ("expansion_deck_composition.jsonl")
)


@dataclass(frozen=True)
class ExpansionCompositionEvidenceValidation:
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


def validate_expansion_composition_evidence_manifest(
    path: Path = EXPANSION_COMPOSITION_EVIDENCE_PATH,
    known_registry_ids: Collection[str] | None = None,
) -> ExpansionCompositionEvidenceValidation:
    if not path.exists():
        return ExpansionCompositionEvidenceValidation(path, "missing", 0, 0, [])
    registry_ids = set(known_registry_ids or catalog_registry_ids())
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
        errors.extend(evidence_entry_errors(entry, line_number, seen, registry_ids))
        if evidence_entry_verified(entry):
            verified += 1
    return ExpansionCompositionEvidenceValidation(
        path,
        "present",
        records,
        verified,
        errors,
    )


__all__ = [
    "EXPANSION_COMPOSITION_EVIDENCE_PATH",
    "ExpansionCompositionEvidenceValidation",
    "validate_expansion_composition_evidence_manifest",
]
