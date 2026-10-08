"""Behavior metadata for Nuclear War cards."""

from __future__ import annotations

from dataclasses import dataclass

from .cards_registry import CardRecord, CardType


@dataclass(frozen=True)
class CardBehavior:
    category: CardType
    metadata: dict[str, object]


def build_behavior_index(cards: dict[str, CardRecord]) -> dict[str, CardBehavior]:
    index: dict[str, CardBehavior] = {}
    for card_id, record in cards.items():
        metadata: dict[str, object]
        if record.type is CardType.WARHEAD:
            metadata = {"yield_megatons": record.data.get("yield_megatons", 0)}
        elif record.type is CardType.CARRIER:
            metadata = {
                "max_yield_megatons": record.data.get("max_yield_megatons", 0),
                "intercept_by": tuple(record.data.get("intercept_by", [])),
            }
            if record.data.get("postal_effect"):
                metadata["postal_effect"] = record.data["postal_effect"]
        elif record.type is CardType.PROPAGANDA:
            metadata = {"value_millions": record.data.get("value_millions", 0)}
        elif record.type is CardType.ANTI_MISSILE:
            metadata = {"label": record.data.get("label")}
        elif record.type in {CardType.SECRET, CardType.TOP_SECRET}:
            effect = record.data.get("effect", {})
            metadata = dict(effect) if isinstance(effect, dict) else {}
        else:
            metadata = dict(record.data)
        index[card_id] = CardBehavior(category=record.type, metadata=metadata)
    return index


__all__ = ["CardBehavior", "build_behavior_index"]
