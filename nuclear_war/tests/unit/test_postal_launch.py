"""Postal launch phase tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.launch import declare_target
from nuclear_war_env.engine.postal.handlers_launch import phase_intercept
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(cards: list[Card]) -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.register_cards(cards)
    state.rng = SeededRNG(seed=0)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _delivery_cards() -> list[Card]:
    return [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]


def test_postal_espionage_and_phase_order() -> None:
    cards = [Card("secret", CardCategory.SECRET, "Secret"), *_delivery_cards()]
    state = _build_state(cards)
    state.players["p2"].secrets = ["secret"]
    state.players["p1"].pending_orders["steal_secret"] = "p2"
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    declare_target(state, "p1", "delivery", "p2")
    events = execute_postal_turn(state)
    phases = [
        event.payload["phase"]
        for event in events
        if event.event_type == "phase_complete"
    ]
    assert phases[0] == "espionage"
    assert state.players["p1"].secrets == ["secret"]
    assert any(event.event_type == "launch_declared" for event in events)


def test_postal_sabotage_blocks_launch() -> None:
    state = _build_state(_delivery_cards())
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    state.players["p1"].pending_orders["targets"] = {"delivery": "p2"}
    state.players["p2"].pending_orders["sabotage"] = [
        {"target": "p1", "delivery": "delivery"}
    ]
    declare_target(state, "p1", "delivery", "p2")
    execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30


def test_postal_intercept_blocks_launch() -> None:
    cards = [
        *_delivery_cards(),
        Card(
            "defense",
            CardCategory.ANTIMISSILE,
            "Defense",
            metadata={"intercept": "any"},
        ),
    ]
    state = _build_state(cards)
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    state.players["p2"].pending_orders["defense"] = ["defense"]
    declare_target(state, "p1", "delivery", "p2")
    execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30
    assert "delivery" not in state.players["p1"].pending_orders.get("launches", {})


def test_postal_intercept_success_payload_matches_replay_schema() -> None:
    cards = [
        *_delivery_cards(),
        Card(
            "defense",
            CardCategory.ANTIMISSILE,
            "Defense",
            metadata={"intercept": "any"},
        ),
    ]
    state = _build_state(cards)
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    state.players["p2"].pending_orders["defense"] = ["defense"]
    declare_target(state, "p1", "delivery", "p2")

    events = phase_intercept(state)

    intercept = next(
        event for event in events if event.event_type == "intercept_success"
    )
    assert intercept.payload == {"stopped_delivery": "delivery"}


def test_postal_final_strike_triggers_attack() -> None:
    state = _build_state(
        [
            Card(
                "delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}
            ),
            Card("warhead", CardCategory.WARHEAD, "Warhead", value=15),
        ]
    )
    state.players["p1"].final_strike_cards = ["warhead"]
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": "p2"}
    ]
    state.players["p2"].pending_orders["sabotage"] = []
    state.players["p2"].pending_orders["targets"] = {}
    execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 15


def test_postal_nuking_applies_fallout() -> None:
    state = _build_state(
        [
            Card(
                "delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}
            ),
            Card("warhead", CardCategory.WARHEAD, "Warhead", value=5),
        ]
    )
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    state.players["p2"].population = [25]
    state.rng = SeededRNG(seed=23)
    execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 10
