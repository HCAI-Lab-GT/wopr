"""Postal equipment setup shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.postal.space_platform import MAX_PLATFORM_WARHEADS
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_atomic_cannon_setup() -> None:
    state = _state([_special("cannon", "atomic_cannon")])
    state.players["p1"].hand = ["cannon"]
    action = _action(state, "postal_atomic_cannon_setup")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    cannon = state.players["p1"].pending_orders["atomic_cannons"]["cannon"]
    assert action.payload == {"card": "cannon", "target": "p2"}
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == [
        "postal_atomic_cannon_setup_ordered"
    ]
    assert cannon["status"] == "ready"
    assert any(event.event_type == "atomic_cannon_setup" for event in postal_events)


def test_postal_legal_actions_can_queue_space_platform_launch() -> None:
    state = _state([_special("platform", "space_platform"), _warhead("w10", 10)])
    state.players["p1"].hand = ["platform", "w10"]
    action = _action(state, "postal_space_platform_launch")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    platform = state.players["p1"].pending_orders["space_platforms"]["platform"]
    assert action.payload == {"card": "platform", "warheads": ["w10"]}
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == [
        "postal_space_platform_launch_ordered"
    ]
    assert platform["warheads"] == [10]
    assert any(event.event_type == "space_platform_launched" for event in postal_events)


def test_space_platform_launch_includes_max_warheads_after_platform() -> None:
    warhead_ids = [f"w{index}" for index in range(MAX_PLATFORM_WARHEADS)]
    cards = [_special("platform", "space_platform")]
    cards.extend(_warhead(card_id, 10) for card_id in warhead_ids)
    state = _state(cards)
    state.players["p1"].hand = ["platform", *warhead_ids]
    action = _action(state, "postal_space_platform_launch")
    assert action.payload == {"card": "platform", "warheads": warhead_ids}


def test_postal_legal_actions_can_queue_space_shuttle_reload() -> None:
    state = _state([_special("shuttle", "space_shuttle"), _warhead("w20", 20)])
    state.players["p1"].hand = ["shuttle", "w20"]
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform": {"warheads": [10]}
    }
    action = _action(state, "postal_space_shuttle_reload")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    platform = state.players["p1"].pending_orders["space_platforms"]["platform"]
    assert action.payload == {
        "card": "shuttle",
        "platform": "platform",
        "warheads": ["w20"],
    }
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == [
        "postal_space_shuttle_reload_ordered"
    ]
    assert platform["warheads"] == [10, 20]
    assert any(event.event_type == "space_shuttle_reloaded" for event in postal_events)


def test_postal_legal_actions_can_queue_space_shuttle_attack() -> None:
    state = _state([_special("shuttle", "space_shuttle"), _warhead("w10", 10)])
    state.players["p1"].hand = ["shuttle", "w10"]
    action = _action(state, "postal_space_shuttle_attack")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {"card": "shuttle", "target": "p2", "warhead": "w10"}
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == [
        "postal_space_shuttle_attack_ordered"
    ]
    assert sum(state.players["p2"].population) == 20
    assert any(event.event_type == "space_shuttle_attacked" for event in postal_events)


def test_postal_legal_actions_can_queue_killer_satellite_launch() -> None:
    state = _state([_special("satellite", "killer_satellite")])
    state.players["p1"].hand = ["satellite"]
    action = _action(state, "postal_killer_satellite_launch")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    satellite = state.players["p1"].pending_orders["killer_satellites"]["satellite"]
    assert action.payload == {"card": "satellite"}
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == [
        "postal_killer_satellite_launch_ordered"
    ]
    assert satellite["status"] == "orbit"
    assert any(
        event.event_type == "killer_satellite_launched" for event in postal_events
    )


def _action(state: GameState, action_type: str):
    matching = [
        action
        for action in legal_actions(state, "p1", mode="postal")
        if action.action_type.value == action_type
    ]
    assert matching
    return matching[0]


def _state(cards: list[Card]) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _special(card_id: str, postal_effect: str) -> Card:
    return Card(
        card_id,
        CardCategory.SPECIAL,
        postal_effect,
        metadata={"postal_effect": postal_effect},
    )


def _warhead(card_id: str, value: int) -> Card:
    return Card(card_id, CardCategory.WARHEAD, "Warhead", value=value)
