"""Postal peace phase tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_peace_vote_counts_live_players_only() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2", "p3"], starting_population=30),
        draw_pile=[],
    )
    state.peace = False
    state.players["p3"].alive = False
    state.players["p3"].population = []
    state.players["p1"].pending_orders["vote_peace"] = True
    state.players["p2"].pending_orders["vote_peace"] = True

    events = execute_postal_turn(state)

    assert state.peace
    assert any(event.event_type == "peace_restored" for event in events)


def test_peacetime_secret_kill_does_not_emit_phantom_peace_restored() -> None:
    from nuclear_war_env.engine.war_state import (
        PEACE_RESTORE_PENDING,
        mark_peace_restore_pending,
        restore_peace_after_completed_eliminations,
    )
    from nuclear_war_env.state import GameState, Ruleset, create_players

    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    assert state.peace is True  # peace was never broken
    mark_peace_restore_pending(state.players["p2"])  # a peacetime non-attack kill

    emitted = restore_peace_after_completed_eliminations(state)

    assert emitted is False  # no phantom peace_restored
    assert state.peace is True
    # flag cleared
    assert PEACE_RESTORE_PENDING not in state.players["p2"].pending_orders


def test_wartime_kill_without_final_strike_still_restores_peace() -> None:
    from nuclear_war_env.engine.war_state import (
        declare_war,
        mark_peace_restore_pending,
        restore_peace_after_completed_eliminations,
    )
    from nuclear_war_env.state import GameState, Ruleset, create_players

    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    declare_war(state)  # peace was broken by an attack
    mark_peace_restore_pending(state.players["p2"])

    emitted = restore_peace_after_completed_eliminations(state)

    assert emitted is True
    assert state.peace is True
    assert all(not p.at_war for p in state.players.values())
