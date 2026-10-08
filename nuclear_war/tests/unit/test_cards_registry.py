"""Tests for card registry and behaviour mapping."""

from __future__ import annotations

from pathlib import Path

import pytest

from nuclear_war_env.card_behaviors import build_behavior_index
from nuclear_war_env.cards_registry import (
    CardRecord,
    CardType,
    build_deck_from_registry,
    card_from_record,
    load_card_registry,
)


def test_registry_counts_and_behaviors() -> None:
    registry = load_card_registry(Path("rules/nuclear_war_base_cards.jsonl"))
    behaviors = build_behavior_index(registry)
    assert len(registry) == len(behaviors)
    assert sum(record.count for record in registry.values()) == 100
    carriers = [
        record for record in registry.values() if record.type is CardType.CARRIER
    ]
    assert carriers
    sample_carrier = behaviors[carriers[0].identifier]
    assert sample_carrier.metadata["intercept_by"]


def test_carrier_registry_preserves_postal_effect_metadata() -> None:
    record = CardRecord(
        identifier="mx",
        name="MX Missile",
        type=CardType.CARRIER,
        count=0,
        data={"postal_effect": "mx_missile", "max_yield_megatons": 100},
    )
    card = card_from_record(record)
    assert card.metadata["postal_effect"] == "mx_missile"


def test_build_deck_from_registry_instantiates_unique_physical_copies() -> None:
    registry = {
        "missile": CardRecord(
            "missile",
            "Missile",
            CardType.CARRIER,
            3,
            {"max_yield_megatons": 100, "intercept_by": ["abm"]},
        )
    }
    deck = build_deck_from_registry(registry)
    assert [card.identifier for card in deck] == [
        "missile__copy_01",
        "missile__copy_02",
        "missile__copy_03",
    ]
    assert [card.metadata["base_card_id"] for card in deck] == ["missile"] * 3
    assert [card.metadata["copy_index"] for card in deck] == [1, 2, 3]


def test_build_deck_from_registry_keeps_singleton_identifier() -> None:
    registry = {
        "abm": CardRecord("abm", "ABM", CardType.ANTI_MISSILE, 1, {"label": "ABM"})
    }
    deck = build_deck_from_registry(registry)
    assert [card.identifier for card in deck] == ["abm"]
    assert deck[0].metadata["base_card_id"] == "abm"
    assert deck[0].metadata["copy_index"] == 1


def test_load_card_registry_rejects_json_constants(tmp_path: Path) -> None:
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        '{"id": NaN, "type": "warhead", "name": "Invalid"}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid JSON constant: NaN"):
        load_card_registry(registry_path)
