"""Postal anti-missile conditional defense order tests."""

from __future__ import annotations

from nuclear_war_env.actions import apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    delivery = Card("delivery", CardCategory.DELIVERY, "Delivery", value=1)
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=10)
    defense = Card(
        "defense",
        CardCategory.ANTIMISSILE,
        "Anti-Missile",
        metadata={"intercept": "any"},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards([delivery, warhead, defense])
    state.population_bank = [10, 5]
    state.players["p2"].hand = ["defense"]
    return state


def _queue_launch(state: GameState) -> None:
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }


def _defense_actions(state: GameState) -> list:
    return [
        action
        for action in legal_actions(state, "p2", mode="postal")
        if action.action_type.value == "postal_defense"
    ]


def test_defense_order_offered_without_visible_incoming_launch() -> None:
    state = _state()

    matching = _defense_actions(state)

    assert matching
    assert matching[0].payload == {"card": "defense"}


def test_defense_order_keeps_card_in_hand_until_used() -> None:
    state = _state()

    events = apply_action(state, _defense_actions(state)[0])

    assert state.players["p2"].hand == ["defense"]
    assert state.players["p2"].pending_orders["defense"] == ["defense"]
    assert [event.event_type for event in events] == ["postal_defense_ordered"]


def test_conditional_defense_order_intercepts_incoming_launch() -> None:
    state = _state()
    apply_action(state, _defense_actions(state)[0])
    _queue_launch(state)

    postal_events = execute_postal_turn(state)

    assert any(event.event_type == "intercept_success" for event in postal_events)
    assert sum(state.players["p2"].population) == 30
    assert state.players["p2"].hand == []
    assert "defense" in {card.identifier for card in state.discard_pile}


def test_hand_antimissile_does_not_auto_intercept_without_order() -> None:
    state = _state()
    _queue_launch(state)

    postal_events = execute_postal_turn(state)

    assert not any(event.event_type == "intercept_success" for event in postal_events)
    assert sum(state.players["p2"].population) == 20
    assert state.players["p2"].hand == ["defense"]


def test_unused_defense_order_expires_at_end_of_turn() -> None:
    state = _state()
    apply_action(state, _defense_actions(state)[0])

    execute_postal_turn(state)

    assert state.players["p2"].hand == ["defense"]
    assert "defense" not in state.players["p2"].pending_orders


def test_dead_defender_defense_order_does_not_intercept() -> None:
    state = _state()
    apply_action(state, _defense_actions(state)[0])
    _queue_launch(state)
    state.players["p2"].alive = False
    state.players["p2"].population = []

    postal_events = execute_postal_turn(state)

    assert not any(event.event_type == "intercept_success" for event in postal_events)
    assert "defense" not in state.players["p2"].pending_orders
    assert "delivery" not in {card.identifier for card in state.discard_pile}


def test_postal_final_strike_does_not_auto_intercept_without_order() -> None:
    state = _state()
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": "p2"}
    ]

    postal_events = execute_postal_turn(state)

    assert not any(event.event_type == "intercept_success" for event in postal_events)
    assert sum(state.players["p2"].population) == 20
    assert state.players["p2"].hand == ["defense"]


def test_postal_final_strike_respects_conditional_defense_order() -> None:
    state = _state()
    apply_action(state, _defense_actions(state)[0])
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": "p2"}
    ]

    postal_events = execute_postal_turn(state)

    assert any(event.event_type == "intercept_success" for event in postal_events)
    assert sum(state.players["p2"].population) == 30
    assert state.players["p2"].hand == []
