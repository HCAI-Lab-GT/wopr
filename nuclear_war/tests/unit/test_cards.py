"""Unit tests for card definitions and deterministic shuffling."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nuclear_war_env.cards import (
    CardCategory,
    count_by_category,
    filter_by_category,
    load_card_definitions,
    shuffle_deck,
)
from nuclear_war_env.rng import SeededRNG


def _write_card_file(directory: Path) -> Path:
    data = [
        {
            "id": "warhead_20",
            "category": "warhead",
            "name": "Warhead 20",
            "value": 20,
            "metadata": {"yield": 20},
        },
        {
            "id": "delivery_bomber",
            "category": "delivery",
            "name": "Bomber",
            "metadata": {"capacity": 3},
        },
        {
            "id": "propaganda_tv",
            "category": "propaganda",
            "name": "TV Appeal",
        },
    ]
    path = directory / "cards.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_card_definitions(tmp_path: Path) -> None:
    card_path = _write_card_file(tmp_path)
    cards = load_card_definitions(card_path)
    assert len(cards) == 3
    assert {card.category for card in cards} == {
        CardCategory.WARHEAD,
        CardCategory.DELIVERY,
        CardCategory.PROPAGANDA,
    }
    bomber = next(card for card in cards if card.identifier == "delivery_bomber")
    assert bomber.metadata["capacity"] == 3


def test_load_card_definitions_rejects_json_constants(tmp_path: Path) -> None:
    card_path = tmp_path / "cards.json"
    card_path.write_text(
        '[{"id": "warhead_nan", "category": "warhead", "value": NaN}]',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid JSON constant: NaN"):
        load_card_definitions(card_path)


def test_shuffle_deterministic(tmp_path: Path) -> None:
    cards = load_card_definitions(_write_card_file(tmp_path))
    rng_a = SeededRNG(seed=42)
    rng_b = SeededRNG(seed=42)
    first = shuffle_deck(cards, rng_a)
    second = shuffle_deck(cards, rng_b)
    assert first == second
    rng_c = SeededRNG(seed=99)
    third = shuffle_deck(cards, rng_c)
    assert first != third


def test_filter_and_counts(tmp_path: Path) -> None:
    cards = load_card_definitions(_write_card_file(tmp_path))
    warheads = filter_by_category(cards, CardCategory.WARHEAD)
    assert len(warheads) == 1
    counts = count_by_category(cards)
    assert counts[CardCategory.WARHEAD] == 1
    assert counts[CardCategory.PROPAGANDA] == 1
