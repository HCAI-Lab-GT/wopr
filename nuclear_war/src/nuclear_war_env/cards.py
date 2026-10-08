"""Card definitions and deck utilities for the Nuclear War engine."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from .rng import SeededRNG


class CardCategory(StrEnum):
    POPULATION = "population"
    WARHEAD = "warhead"
    DELIVERY = "delivery"
    PROPAGANDA = "propaganda"
    ANTIMISSILE = "antimissile"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    SPECIAL = "special"


@dataclass(frozen=True)
class Card:
    """Immutable card record loaded from external definitions."""

    identifier: str
    category: CardCategory
    name: str
    value: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


def load_card_definitions(path: str | Path) -> list[Card]:
    data = json.loads(
        Path(path).read_text(encoding="utf-8"),
        parse_constant=_reject_json_constant,
    )
    cards: list[Card] = []
    for entry in data:
        try:
            category = CardCategory(entry["category"])
        except KeyError as exc:  # pragma: no cover - defensive against bad data
            raise ValueError("Card entry missing category") from exc
        except ValueError as exc:
            raise ValueError(f"Unknown card category: {entry['category']}") from exc
        identifier = entry.get("id") or entry.get("identifier")
        if not identifier:
            raise ValueError("Card entry missing identifier")
        metadata = entry.get("metadata", {})
        cards.append(
            Card(
                identifier=identifier,
                category=category,
                name=entry.get("name", identifier),
                value=entry.get("value"),
                metadata=metadata,
            )
        )
    return cards


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def build_deck(cards: Sequence[Card]) -> list[Card]:
    return list(cards)


def shuffle_deck(cards: Sequence[Card], rng: SeededRNG) -> list[Card]:
    return rng.shuffle(cards)


def filter_by_category(cards: Iterable[Card], category: CardCategory) -> list[Card]:
    return [card for card in cards if card.category is category]


def count_by_category(cards: Iterable[Card]) -> dict[CardCategory, int]:
    totals: dict[CardCategory, int] = {category: 0 for category in CardCategory}
    for card in cards:
        totals[card.category] += 1
    return totals


__all__ = [
    "Card",
    "CardCategory",
    "build_deck",
    "shuffle_deck",
    "filter_by_category",
    "count_by_category",
    "load_card_definitions",
]
