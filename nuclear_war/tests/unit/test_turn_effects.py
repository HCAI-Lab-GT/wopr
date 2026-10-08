"""Turn-effect guard tests."""

from __future__ import annotations

from nuclear_war_env.state import PlayerState
from nuclear_war_env.turn_effects import has_skip_turn


def test_has_skip_turn_ignores_boolean_pending_value() -> None:
    player = PlayerState(player_id="p1", population=[30])
    player.pending_orders["skip_turns"] = True

    assert not has_skip_turn(player)
