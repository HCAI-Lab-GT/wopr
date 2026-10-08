"""Launch engine tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import declare_target, execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players


def _build_state(cards: list[Card]) -> GameState:
    players = create_players(["p1"], starting_population=10)
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=players,
        draw_pile=list(cards),
        rng=SeededRNG(seed=1),
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _launch_state(warhead_value: int = 10) -> GameState:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=warhead_value),
    ]
    state = _build_state(cards)
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    return state


def test_execute_launches_applies_damage() -> None:
    state = _launch_state()
    state.rng = SeededRNG(seed=0)
    events = execute_launches(state)
    defender = state.players["p2"]
    assert sum(defender.population) == 20
    assert not state.peace
    assert any(event.event_type == "warhead_detonated" for event in events)


def test_execute_launches_intercept_prevents_damage() -> None:
    state = _launch_state()
    defense = Card(
        "defense",
        CardCategory.ANTIMISSILE,
        "Defense",
        metadata={"intercept": "any"},
    )
    state.register_cards([defense])
    state.players["p2"].pending_orders["defense"] = ["defense"]
    events = execute_launches(state)
    assert sum(state.players["p2"].population) == 30
    assert any(event.event_type == "intercept_success" for event in events)
    assert not state.peace
    assert state.next_player_id == "p2"


def test_execute_launches_applies_spinner_multiplier() -> None:
    state = _launch_state(warhead_value=5)
    state.players["p2"].population = [25]
    state.rng = SeededRNG(seed=23)
    events = execute_launches(state)
    assert sum(state.players["p2"].population) == 10
    assert any(event.event_type == "spinner_result" for event in events)


def test_spinner_result_logs_randomizer_source() -> None:
    state = _launch_state(warhead_value=5)
    state.rng = SeededRNG(seed=23)
    events = execute_launches(state)
    spinner = next(event for event in events if event.event_type == "spinner_result")
    assert spinner.payload["randomizer"] == "base_two_d10_fallout_chart"
    assert spinner.payload["source_table_id"] == "base_two_d10_fallout_chart"


def test_execute_launches_declares_war_on_dud() -> None:
    state = _launch_state()
    state.players["p3"] = PlayerState(player_id="p3", population=[10])
    state.rng = SeededRNG(seed=2)
    events = execute_launches(state)
    assert sum(state.players["p2"].population) == 30
    assert not state.peace
    assert all(player.at_war for player in state.players.values())
    assert not any(event.event_type == "warhead_detonated" for event in events)


def test_execute_launches_schedules_final_retaliation() -> None:
    cards = [
        Card(
            "delivery_a", CardCategory.DELIVERY, "Delivery A", metadata={"capacity": 1}
        ),
        Card("warhead_a", CardCategory.WARHEAD, "Warhead A", value=30),
        Card(
            "delivery_b", CardCategory.DELIVERY, "Delivery B", metadata={"capacity": 1}
        ),
        Card("warhead_b", CardCategory.WARHEAD, "Warhead B", value=15),
    ]
    state = _build_state(cards)
    state.rng = SeededRNG(seed=0)
    state.players["p2"] = PlayerState(player_id="p2", population=[20])
    state.players["p2"].hand = ["delivery_b", "warhead_b"]
    state.players["p1"].pending_orders["launches"] = {
        "delivery_a": {
            "delivery": "delivery_a",
            "capacity": 1,
            "warheads": ["warhead_a"],
            "target": "p2",
        }
    }
    events = execute_launches(state)
    assert any(event.event_type == "player_eliminated" for event in events)
    assert any(event.event_type == "final_strike_executed" for event in events)


def test_declare_target_sets_launch_target() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1})
    ]
    state = _build_state(cards)
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": [],
            "target": None,
        }
    }
    state.players["p2"] = PlayerState(player_id="p2", population=[10])
    declare_target(state, "p1", "delivery", "p2")
    assert state.players["p1"].pending_orders["launches"]["delivery"]["target"] == "p2"
