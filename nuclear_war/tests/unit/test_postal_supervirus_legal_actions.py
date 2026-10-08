"""Postal Supervirus shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.postal.handlers_misc import phase_cruise_move
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_supervirus_pass() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2", "p3"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.population_bank = [1]
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": 1,
    }

    actions = legal_actions(state, "p2", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_SUPERVIRUS_PASS
    )
    events = apply_action(state, action)
    postal_events = phase_cruise_move(state)

    assert action.payload == {"target": "p3"}
    assert [event.event_type for event in events] == ["postal_supervirus_pass_ordered"]
    assert "supervirus" not in state.players["p2"].pending_orders
    assert state.players["p3"].pending_orders["supervirus"]["source"] == "p2"
    assert any(event.event_type == "supervirus_passed" for event in postal_events)


def test_postal_legal_actions_can_queue_supervirus_start_from_hand() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2", "p3"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.population_bank = [1]
    virus = Card(
        "virus",
        CardCategory.SPECIAL,
        "Supervirus",
        metadata={"postal_effect": "supervirus"},
    )
    state.register_cards([virus])
    state.players["p1"].hand = ["virus"]
    actions = legal_actions(state, "p1", mode="postal")
    matching = [
        item for item in actions if item.action_type.value == "postal_supervirus_start"
    ]
    assert matching
    events = apply_action(state, matching[0])
    postal_events = phase_cruise_move(state)

    assert matching[0].payload == {"card": "virus", "target": "p2"}
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == ["postal_supervirus_start_ordered"]
    assert state.players["p2"].pending_orders["supervirus"]["source"] == "p1"
    assert any(event.event_type == "supervirus_started" for event in postal_events)
