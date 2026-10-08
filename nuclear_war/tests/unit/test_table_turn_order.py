"""Table environment turn-order tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import (
    _advance,
    _RoundStamper,
    pending_decision,
)
from nuclear_war_env.engine.decision import DecisionCursor, TurnPhase
from nuclear_war_env.env_table import TableAECEnv
from nuclear_war_env.fallout import FalloutOutcome, SpinnerEffect
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players
from nuclear_war_env.table_turn import TurnResult


def test_table_env_uses_interceptor_as_next_agent() -> None:
    env = TableAECEnv(seed=1, players=3)
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
        Card(
            "defense",
            CardCategory.ANTIMISSILE,
            "Defense",
            metadata={"intercept": "any"},
        ),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(env.possible_agents, starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=1),
    )
    state.register_cards(cards)
    state.players["player_0"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "player_2",
        }
    }
    state.players["player_2"].hand = ["defense"]
    state.cursor = DecisionCursor("player_0", TurnPhase.INTERCEPT)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()), True)
    env.game_state = state
    env.agent_selection = "player_2"

    env.step(0)

    assert env.agent_selection == "player_2"
    assert env.game_state.next_player_id is None


def test_table_env_reset_uses_pending_decision_for_selection_and_mask() -> None:
    env = TableAECEnv(seed=1, players=3)

    decision = pending_decision(env.game_state)

    assert decision is not None
    assert env.agent_selection == decision.agent_id
    mask = env.observe(env.agent_selection)["action_mask"]
    assert int(mask.sum()) == len(decision.options)


def test_table_env_step_applies_pending_decision_and_selects_next() -> None:
    env = TableAECEnv(seed=1, players=3)
    first = pending_decision(env.game_state)
    assert first is not None

    env.step(0)

    nxt = pending_decision(env.game_state)
    assert nxt is not None
    assert env.agent_selection == nxt.agent_id
    assert pending_decision(env.game_state) != first


def test_table_env_marks_eliminated_player_terminated_before_game_end(
    monkeypatch,
) -> None:
    env = TableAECEnv(seed=1, players=3)
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=20),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(env.possible_agents, starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.players["player_1"].population = [10]
    state.players["player_0"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "player_1",
        }
    }
    state.cursor = DecisionCursor("player_0", TurnPhase.INTERCEPT)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()), True)
    env.game_state = state
    env.agent_selection = "player_1"
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )

    env.step(0)

    assert env.terminations["player_1"] is True
    assert env.terminations["player_0"] is False
    assert env.terminations["player_2"] is False
    assert int(env.observe("player_1")["action_mask"].sum()) == 0


def test_table_env_advances_engine_turn_after_full_cycle() -> None:
    env = TableAECEnv(seed=1, players=2)

    assert env.game_state.turn == 0

    for _ in range(40):
        if env.game_state.turn >= 1:
            break
        env.step(0)

    assert env.game_state.turn == 1


def test_table_env_non_selected_agent_has_empty_action_mask() -> None:
    env = TableAECEnv(seed=1, players=3)
    decision = pending_decision(env.game_state)
    assert decision is not None
    other = next(agent for agent in env.agents if agent != decision.agent_id)

    assert int(env.observe(other)["action_mask"].sum()) == 0
