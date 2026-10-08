"""Simulation tests for pending final strikes."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, LegalAction
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.simulation import SimulationConfig, run_simulation
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_simulation_allows_eliminated_final_strike_actor(
    monkeypatch,
) -> None:
    state = _final_strike_state()

    def use_final_strike_state(_config: SimulationConfig) -> GameState:
        return state

    monkeypatch.setattr(
        "nuclear_war_env.simulation._create_state", use_final_strike_state
    )

    result = run_simulation(
        SimulationConfig(
            mode="postal",
            players=2,
            seed=0,
            agent="heuristic",
            max_turns=1,
        )
    )

    assert any(
        action["action_type"] == "final_strike_target" for action in result["actions"]
    )
    assert result["final_populations"]["p2"] == 15


def test_postal_simulation_waits_for_final_strike_created_by_turn(
    monkeypatch,
) -> None:
    state = _created_final_strike_state()

    def use_created_final_strike_state(_config: SimulationConfig) -> GameState:
        return state

    monkeypatch.setattr(
        "nuclear_war_env.simulation._create_state", use_created_final_strike_state
    )
    monkeypatch.setattr(
        "nuclear_war_env.simulation._build_agent",
        lambda _agent_name, _rng: _PassAgent(),
    )

    result = run_simulation(
        SimulationConfig(
            mode="postal",
            players=2,
            seed=0,
            agent="heuristic",
            max_turns=2,
        )
    )

    assert result["turns"] == 2
    assert any(
        action["action_type"] == "final_strike_target" for action in result["actions"]
    )
    assert result["final_populations"]["player_0"] < 30


class _PassAgent:
    def choose(self, actions: list[LegalAction]) -> LegalAction:
        for action in actions:
            if action.action_type is ActionType.PASS:
                return action
        return actions[0]


def _final_strike_state() -> GameState:
    delivery = Card("delivery", CardCategory.DELIVERY, "Delivery", value=1)
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=15)
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards([delivery, warhead])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p1"].alive = False
    state.players["p1"].population = []
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": None}
    ]
    return state


def _created_final_strike_state() -> GameState:
    cards = [
        Card("delivery_a", CardCategory.DELIVERY, "Delivery A"),
        Card("warhead_a", CardCategory.WARHEAD, "Warhead A", value=30),
        Card(
            "delivery_b",
            CardCategory.DELIVERY,
            "Delivery B",
            metadata={"capacity": 1},
        ),
        Card("warhead_b", CardCategory.WARHEAD, "Warhead B", value=15),
    ]
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["player_0", "player_1"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["player_1"].hand = ["delivery_b", "warhead_b"]
    state.players["player_0"].pending_orders["launches"] = {
        "delivery_a": {
            "delivery": "delivery_a",
            "capacity": 1,
            "warheads": ["warhead_a"],
            "target": "player_1",
        }
    }
    return state
