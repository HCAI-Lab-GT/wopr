"""Postal rules-fidelity repair tests: submarine return, forced cruise drop, immunity.

These cover the 2026-07-01 audit repairs:
- fired submarines automatically return to port after their exposed turn
- return-to-sender cruise missiles force-drop on their owner the next turn
- supervirus immunity blocks reinfection and immune targets leave the action space
"""

from __future__ import annotations

import pytest

from nuclear_war_env.actions import legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.postal.handlers_misc import phase_cruise_move
from nuclear_war_env.replay_postal_action_payload_shapes import (
    validate_postal_defense_payload,
)
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(players: list[str] | None = None) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(players or ["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.population_bank = [10, 5]
    return state


def test_exposed_returning_submarine_reaches_port_next_turn() -> None:
    state = _state()
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"status": "exposed", "returning_to_port": True}
    }

    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]

    assert submarine["status"] == "in_port"
    assert "returning_to_port" not in submarine
    assert any(event.event_type == "submarine_returned" for event in events)


def test_destroyed_submarine_does_not_return_to_port() -> None:
    state = _state()
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"status": "destroyed", "returning_to_port": True}
    }

    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]

    assert submarine["status"] == "destroyed"
    assert not any(event.event_type == "submarine_returned" for event in events)


def test_submarine_fire_exposed_port_reload_cycle() -> None:
    state = _state()
    warhead = Card("warhead", CardCategory.WARHEAD, "20 Megaton", value=20)
    state.register_cards([warhead])
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 10, "status": "at_sea"}
    }
    state.players["p1"].pending_orders["submarines"] = [
        {"submarine": "sub1", "action": "fire"}
    ]

    execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert submarine["status"] == "exposed"

    execute_postal_turn(state)
    assert submarine["status"] == "in_port"

    state.players["p1"].hand = ["warhead"]
    actions = legal_actions(state, "p1", mode="postal")
    reloads = [
        action
        for action in actions
        if action.action_type.value == "postal_submarine_reload"
    ]
    assert reloads
    assert all(action.payload["submarine"] == "sub1" for action in reloads)


def test_returned_cruise_missile_force_drops_on_owner_next_turn() -> None:
    state = _state()
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {
            "target": "p1",
            "yield": 10,
            "visited": ["p2"],
            "drop_next_turn": True,
        }
    }

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "cruise1" not in state.players["p1"].pending_orders["cruise_missiles"]
    assert "cruise_dropped" in event_types
    assert sum(state.players["p1"].population) == 20


def test_move_order_cannot_cancel_forced_cruise_self_drop() -> None:
    state = _state()
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {
            "target": "p1",
            "yield": 10,
            "visited": ["p2"],
            "drop_next_turn": True,
        }
    }
    state.players["p1"].pending_orders["cruise_move"] = [
        {"missile": "cruise1", "target": "p2"}
    ]

    events = phase_cruise_move(state)
    event_types = [event.event_type for event in events]

    assert "cruise1" not in state.players["p1"].pending_orders["cruise_missiles"]
    assert "cruise_dropped" in event_types
    assert sum(state.players["p1"].population) == 20


def test_doomed_cruise_missile_offers_no_actions() -> None:
    state = _state()
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {
            "target": "p1",
            "yield": 10,
            "visited": ["p2"],
            "drop_next_turn": True,
        }
    }

    actions = legal_actions(state, "p1", mode="postal")
    cruise_actions = [
        action
        for action in actions
        if action.action_type.value in {"postal_cruise_drop", "postal_cruise_move"}
    ]

    assert cruise_actions == []


def test_supervirus_start_skips_immune_target() -> None:
    state = _state(["p1", "p2", "p3"])
    state.register_cards([Card("virus", CardCategory.SPECIAL, "Supervirus")])
    state.players["p2"].pending_orders["supervirus_immunity"] = True
    state.players["p1"].pending_orders["supervirus_start"] = {
        "card": "virus",
        "target": "p2",
    }

    phase_cruise_move(state)

    assert sum(state.players["p2"].population) == 30
    assert "supervirus" not in state.players["p2"].pending_orders


def test_supervirus_pass_to_immune_target_fails_and_holder_retains() -> None:
    state = _state(["p1", "p2", "p3"])
    state.register_cards([Card("virus", CardCategory.SPECIAL, "Supervirus")])
    state.players["p3"].pending_orders["supervirus_immunity"] = True
    state.players["p1"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p2",
        "turns_held": 1,
    }
    state.players["p1"].pending_orders["supervirus_pass"] = {"target": "p3"}

    events = phase_cruise_move(state)
    event_types = [event.event_type for event in events]

    assert "supervirus_pass_failed" in event_types
    assert sum(state.players["p3"].population) == 30
    assert state.players["p1"].pending_orders["supervirus"]["turns_held"] == 2


def test_supervirus_actions_exclude_immune_targets() -> None:
    state = _state(["p1", "p2", "p3"])
    virus = Card(
        "virus",
        CardCategory.SPECIAL,
        "Supervirus",
        metadata={"postal_effect": "supervirus"},
    )
    state.register_cards([virus])
    state.players["p2"].pending_orders["supervirus_immunity"] = True
    state.players["p1"].hand = ["virus"]
    state.players["p1"].pending_orders["supervirus"] = {
        "card": "virus2",
        "source": "p3",
        "turns_held": 1,
    }

    actions = legal_actions(state, "p1", mode="postal")
    virus_targets = {
        str(action.payload["target"])
        for action in actions
        if action.action_type.value
        in {"postal_supervirus_start", "postal_supervirus_pass"}
    }

    assert "p2" not in virus_targets
    assert "p3" in virus_targets


def test_postal_defense_payload_accepts_conditional_and_legacy_shapes() -> None:
    validate_postal_defense_payload({"card": "defense"}, 0)
    validate_postal_defense_payload(
        {"card": "defense", "attacker": "p1", "delivery": "delivery"}, 0
    )
    with pytest.raises(ValueError):
        validate_postal_defense_payload({"card": "defense", "attacker": "p1"}, 0)
