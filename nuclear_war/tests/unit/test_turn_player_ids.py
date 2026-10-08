"""Turn-order generator tests (anti-missile turn-order jump)."""

from __future__ import annotations

from nuclear_war_env.simulation_turns import turn_player_ids
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(player_ids: list[str]) -> GameState:
    return GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(player_ids, starting_population=30),
        draw_pile=[],
    )


def test_turn_player_ids_yields_each_player_once_clockwise() -> None:
    state = _state(["player_0", "player_1", "player_2"])
    assert list(turn_player_ids(state)) == ["player_0", "player_1", "player_2"]


def test_intercept_jump_moves_interceptor_up_without_skipping_anyone() -> None:
    state = _state(["player_0", "player_1", "player_2"])
    yielded: list[str] = []
    for player_id in turn_player_ids(state):
        yielded.append(player_id)
        if player_id == "player_0":
            # Simulate an anti-missile interception by player_2 during player_0's
            # turn: the interceptor should act next, but no one may be skipped.
            state.next_player_id = "player_2"
    assert yielded == ["player_0", "player_2", "player_1"]
    # Every living player acted exactly once: no skip, no duplicate.
    assert sorted(yielded) == ["player_0", "player_1", "player_2"]


def test_intercept_by_already_acted_player_does_not_duplicate_turn() -> None:
    state = _state(["player_0", "player_1", "player_2"])
    yielded: list[str] = []
    for player_id in turn_player_ids(state):
        yielded.append(player_id)
        if player_id == "player_1":
            # player_0 already acted this round; it must not get a second turn.
            state.next_player_id = "player_0"
    assert yielded == ["player_0", "player_1", "player_2"]
