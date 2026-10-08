"""Table AEC final-strike lifecycle tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import _advance, _RoundStamper, pending_decision
from nuclear_war_env.engine.decision import DecisionCursor, DecisionType, TurnPhase
from nuclear_war_env.env_table import TableAECEnv
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players
from nuclear_war_env.table_turn import TurnResult


def _final_strike_state(agent_ids: list[str]) -> GameState:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=15),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(agent_ids, starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["player_1"].alive = False
    state.players["player_1"].population = []
    state.players["player_1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": None}
    ]
    return state


def _prime_final_strike_decision(env: TableAECEnv, state: GameState) -> None:
    state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()), True)
    decision = pending_decision(state)
    assert decision is not None
    assert decision.decision_type is DecisionType.FINAL_STRIKE_TARGET
    env.game_state = state
    env.agent_selection = decision.agent_id


def _advance_without_live_targets(state: GameState) -> list[str]:
    state.cursor = DecisionCursor("player_1", TurnPhase.ATTACK)
    state.cursor.round_pending = set(state.players)
    stamper = _RoundStamper(TurnResult())
    _advance(state, stamper, True)
    return [event.event_type for event, _turn in stamper.events]


def test_table_env_waits_for_active_final_strike_launch_before_done() -> None:
    env = TableAECEnv(seed=1, players=2)
    _prime_final_strike_decision(env, _final_strike_state(env.possible_agents))

    env.step(0)

    assert env.terminations["player_1"] is False
    assert env.agent_selection == "player_0"
    decision = pending_decision(env.game_state)
    assert decision is not None
    assert decision.decision_type is DecisionType.INTERCEPT
    assert int(env.observe("player_0")["action_mask"].sum()) > 0


def test_table_env_resolves_targeted_pending_final_strike() -> None:
    env = TableAECEnv(seed=1, players=2)
    _prime_final_strike_decision(env, _final_strike_state(env.possible_agents))

    env.step(0)
    assert "final_strike_executed" in env.infos["player_1"]["events"]

    env.step(0)

    assert not env.game_state.players["player_1"].pending_orders.get("final_strike")
    assert all(env.terminations.values())


def test_table_env_clears_pending_final_strike_without_live_targets() -> None:
    env = TableAECEnv(seed=1, players=2)
    state = _final_strike_state(env.possible_agents)
    state.players["player_0"].alive = False
    state.players["player_0"].population = []
    events = _advance_without_live_targets(state)
    env.game_state = state
    env.agent_selection = "player_1"

    env.step(0)

    assert "final_strike_executed" in events
    assert not env.game_state.players["player_1"].pending_orders.get("final_strike")
    assert all(env.terminations.values())
