"""Setup variant plumbing tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.setup_game import create_game_state


def test_create_game_state_accepts_active_variant_id() -> None:
    state = create_game_state(
        "table",
        player_count=2,
        seed=0,
        variant_id="base_later_two_d10",
    )

    assert state.variant_id == "base_later_two_d10"


def test_create_game_state_rejects_deferred_variant_before_loading_rules(
    monkeypatch,
) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for deferred variant")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    with pytest.raises(ValueError, match="classic_spinner_scan is deferred"):
        create_game_state(
            "table",
            player_count=2,
            seed=0,
            variant_id="classic_spinner_scan",
        )
