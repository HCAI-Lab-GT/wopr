"""Public-safe source evidence target export."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from .cards_registry import CardRecord, load_card_registry
from .expansions import EXPANSION_MECHANICS, ExpansionMechanic

_RULES_PATH = (
    Path(__file__).resolve().parents[2] / "rules" / "nuclear_war_base_cards.jsonl"
)


class CardEffectTarget(TypedDict):
    card_id: str
    card_name: str
    card_type: str
    count: int


class ExpansionCompositionTarget(TypedDict):
    registry_id: str
    postal_effect: str
    supported_modes: list[str]


class SourceEvidenceTargetsPayload(TypedDict):
    card_effect_target_count: int
    card_effect_targets: list[CardEffectTarget]
    expansion_composition_target_count: int
    expansion_composition_targets: list[ExpansionCompositionTarget]


def source_evidence_targets_payload(
    registry_path: Path = _RULES_PATH,
) -> SourceEvidenceTargetsPayload:
    card_targets = [
        _card_effect_target(record)
        for record in load_card_registry(registry_path).values()
        if _active_count(record.count)
    ]
    expansion_targets = [
        _expansion_composition_target(mechanic) for mechanic in EXPANSION_MECHANICS
    ]
    return {
        "card_effect_target_count": len(card_targets),
        "card_effect_targets": card_targets,
        "expansion_composition_target_count": len(expansion_targets),
        "expansion_composition_targets": expansion_targets,
    }


def _card_effect_target(record: CardRecord) -> CardEffectTarget:
    return {
        "card_id": record.identifier,
        "card_name": record.name,
        "card_type": record.type.value,
        "count": record.count,
    }


def _expansion_composition_target(
    mechanic: ExpansionMechanic,
) -> ExpansionCompositionTarget:
    return {
        "registry_id": mechanic.registry_id,
        "postal_effect": mechanic.postal_effect,
        "supported_modes": list(mechanic.supported_modes),
    }


def _active_count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


__all__ = [
    "CardEffectTarget",
    "ExpansionCompositionTarget",
    "SourceEvidenceTargetsPayload",
    "source_evidence_targets_payload",
]
