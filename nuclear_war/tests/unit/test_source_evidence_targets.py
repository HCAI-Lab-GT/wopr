"""Source evidence target export tests."""

from __future__ import annotations

from nuclear_war_env.cards_registry import load_card_registry
from nuclear_war_env.expansions import EXPANSION_MECHANICS
from nuclear_war_env.rules import RULES_PATH
from nuclear_war_env.source_evidence_targets import source_evidence_targets_payload


def test_source_evidence_targets_are_public_safe_registry_targets() -> None:
    registry = load_card_registry(RULES_PATH)

    payload = source_evidence_targets_payload()

    card_targets = payload["card_effect_targets"]
    expected_cards = [
        record
        for record in registry.values()
        if isinstance(record.count, int) and record.count > 0
    ]
    assert len(card_targets) == len(expected_cards)
    assert card_targets[0] == {
        "card_id": expected_cards[0].identifier,
        "card_name": expected_cards[0].name,
        "card_type": expected_cards[0].type.value,
        "count": expected_cards[0].count,
    }
    assert payload["card_effect_target_count"] == len(expected_cards)


def test_source_evidence_targets_include_expansion_catalog_targets() -> None:
    payload = source_evidence_targets_payload()

    expansion_targets = payload["expansion_composition_targets"]
    assert len(expansion_targets) == len(EXPANSION_MECHANICS)
    assert expansion_targets[0] == {
        "registry_id": EXPANSION_MECHANICS[0].registry_id,
        "postal_effect": EXPANSION_MECHANICS[0].postal_effect,
        "supported_modes": list(EXPANSION_MECHANICS[0].supported_modes),
    }
    assert payload["expansion_composition_target_count"] == len(EXPANSION_MECHANICS)


def test_source_evidence_targets_do_not_include_evidence_material() -> None:
    payload_text = str(source_evidence_targets_payload()).lower()

    assert "source_photo_or_file" not in payload_text
    assert "source_reference" not in payload_text
    assert "private/" not in payload_text
    assert "effect_summary" not in payload_text
