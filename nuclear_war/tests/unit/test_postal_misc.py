"""Postal miscellaneous phase tests."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.launch import declare_target
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(cards: list[Card]) -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.register_cards(cards)
    state.rng = SeededRNG(seed=0)
    return state


def test_postal_propaganda_requires_peace() -> None:
    state = _build_state([])
    state.peace = False
    state.players["p1"].pending_orders["propaganda"] = ["prop_card"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"prop_card": "p2"}
    execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30


def test_postal_peace_restores_after_elimination_without_final_strike() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=30),
    ]
    state = _build_state(cards)
    state.players["p2"].population = [20]
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

    assert state.peace
    assert not any(player.at_war for player in state.players.values())
    assert any(event.event_type == "peace_restored" for event in events)


def test_postal_propaganda_conserves_population_bank_cards() -> None:
    card = Card(
        "prop",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 3},
    )
    state = _build_state([card])
    state.players["p1"].population = [1]
    state.players["p2"].population = [5]
    state.population_bank = [2, 2, 1]
    state.players["p1"].pending_orders["propaganda"] = ["prop"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"prop": "p2"}

    events = execute_postal_turn(state)

    assert state.players["p1"].population == [2, 1, 1]
    assert state.players["p2"].population == [2]
    assert Counter(state.population_bank) == Counter([5])
    assert any(
        event.event_type == "propaganda_effect" and event.payload.get("migrated") == 3
        for event in events
    )


def test_postal_propaganda_elimination_emits_player_eliminated() -> None:
    card = Card(
        "prop",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 5},
    )
    state = _build_state([card])
    state.players["p1"].population = [1]
    state.players["p2"].population = [5]
    state.population_bank = [5]
    state.players["p1"].pending_orders["propaganda"] = ["prop"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"prop": "p2"}

    events = execute_postal_turn(state)

    assert [
        event.event_type
        for event in events
        if event.event_type
        in {
            "propaganda_effect",
            "player_eliminated",
        }
    ] == ["propaganda_effect", "player_eliminated"]
    eliminated = next(
        event for event in events if event.event_type == "player_eliminated"
    )
    assert eliminated.player_id == "p2"
    assert eliminated.payload == {"by": "p1"}


def test_postal_propaganda_ignores_dead_actor_orders() -> None:
    card = Card(
        "prop",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 5},
    )
    state = _build_state([card])
    state.players["p1"].alive = False
    state.players["p1"].population = []
    state.players["p2"].population = [5]
    state.population_bank = [5]
    state.players["p1"].pending_orders["propaganda"] = ["prop"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"prop": "p2"}

    events = execute_postal_turn(state)

    assert state.players["p1"].population == []
    assert state.players["p2"].population == [5]
    assert not any(event.event_type == "propaganda_effect" for event in events)


def test_postal_secret_elimination_emits_player_eliminated() -> None:
    card = Card(
        "secret",
        CardCategory.TOP_SECRET,
        "Supergerm",
        metadata={"damage_population_millions": 25},
    )
    state = _build_state([card])
    state.players["p1"].secrets = ["secret"]
    state.players["p1"].pending_orders["secret_targets"] = {"secret": "p2"}
    state.players["p2"].population = [20]
    state.population_bank = [5]

    events = execute_postal_turn(state)

    assert any(
        event.event_type == "player_eliminated"
        and event.player_id == "p2"
        and event.payload == {"by": "p1"}
        for event in events
    )


def test_postal_secrets_ignore_dead_actor_orders() -> None:
    killer = Card(
        "killer",
        CardCategory.TOP_SECRET,
        "Supergerm",
        metadata={"damage_population_millions": 25},
    )
    steal = Card(
        "steal",
        CardCategory.SECRET,
        "Raises Taxes",
        metadata={"steal_population_millions": 5},
    )
    state = _build_state([killer, steal])
    state.players["p1"].secrets = ["killer"]
    state.players["p1"].pending_orders["secret_targets"] = {"killer": "p2"}
    state.players["p2"].secrets = ["steal"]
    state.players["p2"].pending_orders["secret_targets"] = {"steal": "p1"}
    state.players["p2"].population = [20]
    state.population_bank = [5]

    events = execute_postal_turn(state)

    assert state.players["p2"].population == []
    assert not any(
        event.event_type == "secret_population_stolen" and event.player_id == "p2"
        for event in events
    )


def test_postal_submarine_and_cruise_events() -> None:
    state = _build_state([])
    state.players["p2"].population = [20]
    state.population_bank = [10, 5]
    state.players["p1"].pending_orders["submarines"] = [{"target": "p2", "yield": 5}]
    state.players["p1"].pending_orders["cruise_move"] = [
        {"missile": "cruise1", "target": "p2"},
        {"missile": "cruise2", "target": "p3"},
    ]
    execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 15


def test_postal_legacy_submarine_returns_population_cards_to_bank() -> None:
    state = _build_state([])
    state.players["p2"].population = [5]
    state.population_bank = [2, 1, 1, 1]
    state.players["p1"].pending_orders["submarines"] = [{"target": "p2", "yield": 3}]

    events = execute_postal_turn(state)

    assert state.players["p2"].population == [2]
    assert Counter(state.population_bank) == Counter([5, 1, 1, 1])
    assert any(
        event.event_type == "submarine_strike" and event.payload.get("loss") == 3
        for event in events
    )


def test_submarine_fire_exposes_submarine() -> None:
    state = _build_state([])
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 5, "status": "at_sea"}
    }
    state.players["p1"].pending_orders["submarines"] = [
        {"submarine": "sub1", "action": "fire"}
    ]
    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert sum(state.players["p2"].population) < 30
    assert submarine["status"] == "exposed"
    assert submarine["returning_to_port"] is True
    assert any(event.event_type == "submarine_strike" for event in events)


def test_submarine_returns_to_port_without_exposure() -> None:
    state = _build_state([])
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 10, "status": "at_sea"}
    }
    state.players["p1"].pending_orders["submarines"] = [
        {"submarine": "sub1", "action": "return_to_port"}
    ]
    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert sum(state.players["p2"].population) == 30
    assert submarine["status"] == "in_port"
    assert "returning_to_port" not in submarine
    assert any(event.event_type == "submarine_returned" for event in events)


def test_cruise_move_to_visited_country_returns_to_sender() -> None:
    state = _build_state([])
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "visited": ["p2"]}
    }
    state.players["p1"].pending_orders["cruise_move"] = [
        {"missile": "cruise1", "target": "p2"}
    ]
    events = execute_postal_turn(state)
    missile = state.players["p1"].pending_orders["cruise_missiles"]["cruise1"]
    assert missile["target"] == "p1"
    assert missile["drop_next_turn"] is True
    assert any(
        event.event_type == "cruise_move"
        and event.payload["status"] == "return_to_sender"
        for event in events
    )


def test_cruise_without_move_order_returns_to_sender() -> None:
    state = _build_state([])
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "visited": ["p2"]}
    }
    events = execute_postal_turn(state)
    missile = state.players["p1"].pending_orders["cruise_missiles"]["cruise1"]
    assert missile["target"] == "p1"
    assert missile["drop_next_turn"] is True
    assert any(
        event.event_type == "cruise_move"
        and event.payload["status"] == "return_to_sender"
        for event in events
    )


def test_postal_specials_logged() -> None:
    state = _build_state([])
    state.players["p1"].pending_orders["specials"] = ["special_card"]
    events = execute_postal_turn(state)
    assert any(event.event_type == "special_played" for event in events)


def test_postal_no_press_discards_press_without_event() -> None:
    state = _build_state([])
    state.players["p1"].pending_orders["press"] = ["hello"]
    events = execute_postal_turn(state)
    assert "press" not in state.players["p1"].pending_orders
    assert not any(event.event_type == "press_entry" for event in events)
