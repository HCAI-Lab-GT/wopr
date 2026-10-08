"""Utilities for loading and classifying Nuclear War cards."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .cards import Card, CardCategory


class CardType(StrEnum):
    WARHEAD = "warhead"
    CARRIER = "carrier"
    PROPAGANDA = "propaganda"
    ANTI_MISSILE = "anti_missile"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    SPECIAL = "special"


@dataclass(frozen=True)
class CardRecord:
    identifier: str
    name: str
    type: CardType
    count: int
    data: dict[str, Any]


def load_card_registry(path: Path) -> dict[str, CardRecord]:
    registry: dict[str, CardRecord] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            entry = json.loads(line, parse_constant=_reject_json_constant)
            card_type = CardType(entry["type"])
            registry[entry["id"]] = CardRecord(
                identifier=entry["id"],
                name=entry.get("name"),
                type=card_type,
                count=entry.get("count_in_deck", 1),
                data=entry,
            )
    return registry


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def card_from_record(record: CardRecord) -> Card:
    meta = record.data
    if record.type is CardType.WARHEAD:
        value = meta.get("yield_megatons")
        metadata = {"yield_megatons": value}
        category = CardCategory.WARHEAD
    elif record.type is CardType.CARRIER:
        metadata = {
            "max_yield_megatons": meta.get("max_yield_megatons", 0),
            "intercept_by": tuple(meta.get("intercept_by", [])),
        }
        if meta.get("postal_effect"):
            metadata["postal_effect"] = meta["postal_effect"]
        category = CardCategory.DELIVERY
        value = None
    elif record.type is CardType.PROPAGANDA:
        metadata = {"value_millions": meta.get("value_millions", 0)}
        category = CardCategory.PROPAGANDA
        value = meta.get("value_millions")
    elif record.type is CardType.ANTI_MISSILE:
        metadata = {"label": meta.get("label")}
        category = CardCategory.ANTIMISSILE
        value = None
    elif record.type is CardType.SECRET:
        metadata = meta.get("effect", {})
        category = CardCategory.SECRET
        value = None
    elif record.type is CardType.TOP_SECRET:
        metadata = meta.get("effect", {})
        category = CardCategory.TOP_SECRET
        value = None
    else:
        metadata = meta
        category = CardCategory.SPECIAL
        value = None
    return Card(
        identifier=record.identifier,
        category=category,
        name=record.name,
        value=value,
        metadata=metadata,
    )


def _deck_card_from_record(
    record: CardRecord,
    copy_index: int,
    copy_count: int,
) -> Card:
    card = card_from_record(record)
    metadata = dict(card.metadata)
    metadata["base_card_id"] = record.identifier
    metadata["copy_index"] = copy_index
    identifier = record.identifier
    if copy_count > 1:
        identifier = f"{record.identifier}__copy_{copy_index:02d}"
    return Card(
        identifier=identifier,
        category=card.category,
        name=card.name,
        value=card.value,
        metadata=metadata,
    )


def build_deck_from_registry(registry: dict[str, CardRecord]) -> list[Card]:
    deck: list[Card] = []
    for record in registry.values():
        for copy_index in range(1, record.count + 1):
            deck.append(_deck_card_from_record(record, copy_index, record.count))
    return deck


__all__ = [
    "CardType",
    "CardRecord",
    "load_card_registry",
    "card_from_record",
    "build_deck_from_registry",
]
