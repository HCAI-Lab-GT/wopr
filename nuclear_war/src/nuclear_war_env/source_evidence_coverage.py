"""Source evidence target coverage reporting."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .card_effect_evidence import CARD_EFFECT_EVIDENCE_PATH
from .card_effect_evidence_rules import (
    evidence_entry_verified as card_effect_entry_verified,
)
from .card_effect_evidence_rules import (
    reject_json_constant as reject_card_json_constant,
)
from .cards_registry import CardRecord, load_card_registry
from .expansion_composition_evidence import EXPANSION_COMPOSITION_EVIDENCE_PATH
from .expansion_composition_evidence_rules import (
    evidence_entry_verified as expansion_entry_verified,
)
from .expansion_composition_evidence_rules import (
    reject_json_constant as reject_expansion_json_constant,
)
from .expansions import EXPANSION_MECHANICS

_RULES_PATH = (
    Path(__file__).resolve().parents[2] / "rules" / "nuclear_war_base_cards.jsonl"
)


@dataclass(frozen=True)
class SourceEvidenceCoverage:
    required_ids: tuple[str, ...]
    recorded_ids: tuple[str, ...]
    verified_ids: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "target_count": len(self.required_ids),
            "required_ids": list(self.required_ids),
            "recorded_count": len(self.recorded_ids),
            "recorded_ids": list(self.recorded_ids),
            "verified_count": len(self.verified_ids),
            "verified_ids": list(self.verified_ids),
            "missing_ids": self.missing_ids(),
            "unverified_ids": self.unverified_ids(),
        }

    def missing_ids(self) -> list[str]:
        recorded = set(self.recorded_ids)
        return [item for item in self.required_ids if item not in recorded]

    def unverified_ids(self) -> list[str]:
        verified = set(self.verified_ids)
        return [item for item in self.recorded_ids if item not in verified]


def card_effect_evidence_coverage(
    path: Path = CARD_EFFECT_EVIDENCE_PATH,
    registry_path: Path = _RULES_PATH,
) -> SourceEvidenceCoverage:
    return card_effect_evidence_coverage_for_registry(
        path,
        load_card_registry(registry_path),
    )


def card_effect_evidence_coverage_for_registry(
    path: Path,
    registry: Mapping[str, CardRecord],
) -> SourceEvidenceCoverage:
    required_ids = tuple(
        record.identifier for record in registry.values() if _active_count(record.count)
    )
    recorded_ids, verified_ids = _manifest_ids(
        path,
        "card_id",
        card_effect_entry_verified,
        reject_card_json_constant,
    )
    return _coverage(required_ids, recorded_ids, verified_ids)


def expansion_composition_evidence_coverage(
    path: Path = EXPANSION_COMPOSITION_EVIDENCE_PATH,
) -> SourceEvidenceCoverage:
    required_ids = tuple(mechanic.registry_id for mechanic in EXPANSION_MECHANICS)
    recorded_ids, verified_ids = _manifest_ids(
        path,
        "registry_id",
        expansion_entry_verified,
        reject_expansion_json_constant,
    )
    return _coverage(required_ids, recorded_ids, verified_ids)


def _coverage(
    required_ids: tuple[str, ...],
    recorded_ids: set[str],
    verified_ids: set[str],
) -> SourceEvidenceCoverage:
    recorded = tuple(item for item in required_ids if item in recorded_ids)
    verified = tuple(item for item in required_ids if item in verified_ids)
    return SourceEvidenceCoverage(required_ids, recorded, verified)


def _manifest_ids(
    path: Path,
    id_field: str,
    entry_verified: Callable[[dict[str, Any]], bool],
    reject_json_constant: Callable[[str], None],
) -> tuple[set[str], set[str]]:
    if not path.exists():
        return set(), set()
    recorded_ids: set[str] = set()
    verified_ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        try:
            entry = json.loads(line, parse_constant=reject_json_constant)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(entry, dict):
            continue
        identifier = entry.get(id_field)
        if not isinstance(identifier, str) or not identifier:
            continue
        recorded_ids.add(identifier)
        if entry_verified(entry):
            verified_ids.add(identifier)
    return recorded_ids, verified_ids


def _active_count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


__all__ = [
    "SourceEvidenceCoverage",
    "card_effect_evidence_coverage",
    "card_effect_evidence_coverage_for_registry",
    "expansion_composition_evidence_coverage",
]
