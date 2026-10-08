"""Expansion mechanic catalog tests."""

from __future__ import annotations

import pytest

from nuclear_war_env import expansions
from nuclear_war_env.action_models import ActionType
from nuclear_war_env.expansions import (
    EXPANSION_MECHANICS,
    ExpansionMechanic,
    catalog_mode_gaps,
)


def test_expansion_catalog_lists_postal_metadata_effects() -> None:
    assert {item.postal_effect for item in EXPANSION_MECHANICS} == {
        "atomic_cannon",
        "cruise_missile",
        "killer_satellite",
        "mx_missile",
        "sabotage",
        "smart_bomb",
        "space_platform",
        "space_shuttle",
        "submarine",
        "supervirus",
    }


def test_expansion_catalog_action_types_exist() -> None:
    action_values = {item.value for item in ActionType}
    for mechanic in EXPANSION_MECHANICS:
        assert set(mechanic.action_types) <= action_values


def test_expansion_catalog_is_postal_only_until_source_verified() -> None:
    assert {item.supported_modes for item in EXPANSION_MECHANICS} == {("postal",)}


def test_expansion_catalog_mode_gaps_report_empty_and_unknown_modes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        expansions,
        "EXPANSION_MECHANICS",
        (
            ExpansionMechanic("empty", "empty_card", ()),
            ExpansionMechanic("unknown", "unknown_card", ("postal", "future")),
        ),
    )

    assert catalog_mode_gaps() == [
        {"postal_effect": "unknown", "mode": "future"},
        {"postal_effect": "empty", "mode": "<empty>"},
    ]
