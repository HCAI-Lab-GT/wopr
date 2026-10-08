"""Unit tests for the faithful table turn driver."""

from __future__ import annotations

from nuclear_war_agents.baseline import HeuristicAgent
from nuclear_war_env.hand_count import draw_count
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.setup_game import create_game_state
from nuclear_war_env.state import HAND_LIMIT
from nuclear_war_env.table_turn import play_table_turn


def test_play_table_turn_slides_track_and_places_a_card() -> None:
    state = create_game_state("table", player_count=2, seed=3)
    agent = HeuristicAgent(SeededRNG(0))
    player = state.players["player_0"]

    result = play_table_turn(state, "player_0", agent)

    # The launch track stays full: one card slid out and resolved, one placed in.
    assert sum(1 for card_id in player.face_down_queue if card_id is not None) == 2
    assert any(event.event_type == "cards_enqueued" for event in result.events)
    # One card left the counted pool this turn (the resolved face-up card).
    assert draw_count(player) == HAND_LIMIT - 1


def test_play_table_turn_redraws_to_target_at_start_of_next_turn() -> None:
    state = create_game_state("table", player_count=2, seed=3)
    agent = HeuristicAgent(SeededRNG(0))

    play_table_turn(state, "player_0", agent)  # ends one below the draw target
    result = play_table_turn(state, "player_0", agent)

    # The mandatory draw step refills the hand to the target every turn.
    assert any(event.event_type == "card_drawn" for event in result.events)
