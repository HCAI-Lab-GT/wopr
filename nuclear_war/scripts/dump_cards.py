#!/usr/bin/env python3
"""Utility script to inspect card registry."""

from __future__ import annotations

from pathlib import Path

from nuclear_war_env.cards_registry import CardType, load_card_registry


def main() -> None:
    registry = load_card_registry(Path("rules/nuclear_war_base_cards.jsonl"))
    counts: dict[CardType, int] = {card_type: 0 for card_type in CardType}
    for record in registry.values():
        counts[record.type] += record.count
    for card_type, count in counts.items():
        print(f"{card_type.value}: {count}")


if __name__ == "__main__":
    main()
