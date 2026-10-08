"""Simulation replay safety tests for pending final strikes."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, LegalAction
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.replay import write_replay
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.simulation import SimulationConfig, run_simulation
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_pending_final_strike_max_turn_result_is_replay_safe(
    monkeypatch,
    tmp_path,
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
            max_turns=1,
        )
    )

    assert result["termination_reason"] == "max_turns"
    assert result["final_populations"] == {"player_0": 30, "player_1": 0}
    write_replay(tmp_path / "pending_final_strike.json", result)


class _PassAgent:
    def choose(self, actions: list[LegalAction]) -> LegalAction:
        for action in actions:
            if action.action_type is ActionType.PASS:
                return action
        return actions[0]


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
