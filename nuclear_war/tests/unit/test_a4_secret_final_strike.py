from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import (
    _advance,
    _RoundStamper,
    apply_decision,
    pending_decision,
)
from nuclear_war_env.engine.decision import DecisionCursor, DecisionType, TurnPhase
from nuclear_war_env.fallout import FalloutOutcome, SpinnerEffect
from nuclear_war_env.state import GameState, Ruleset, create_players
from nuclear_war_env.table_turn import TurnResult


def _secret_final_strike_state() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["player_0", "player_1", "player_2"], 30),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card(
                "secret",
                CardCategory.SECRET,
                "Secret Damage",
                metadata={"damage_population_millions": 30},
            ),
            Card(
                "delivery",
                CardCategory.DELIVERY,
                "Delivery",
                metadata={"capacity": 1},
            ),
            Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
        ]
    )
    state.players["player_0"].secrets = ["secret"]
    state.players["player_1"].hand = ["delivery", "warhead"]
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.cursor = DecisionCursor("player_0", TurnPhase.SECRETS)
    state.cursor.round_pending = set(state.players)
    return state


def test_secret_elimination_queues_final_strike_decision() -> None:
    state = _secret_final_strike_state()
    _advance(state, _RoundStamper(TurnResult()), True)
    secret = pending_decision(state)
    assert secret is not None
    assert secret.decision_type is DecisionType.SECRET_TARGET

    events = apply_decision(state, secret.options[0])
    decision = pending_decision(state)

    assert "final_strike_executed" not in [event.event_type for event in events]
    assert state.players["player_1"].pending_orders.get("final_strike")
    assert decision is not None
    assert decision.decision_type is DecisionType.FINAL_STRIKE_TARGET
    assert decision.agent_id == "player_1"


def test_secret_triggered_final_strike_resumes_interrupted_turn(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )
    state = _secret_final_strike_state()
    _advance(state, _RoundStamper(TurnResult()), True)
    secret = pending_decision(state)
    assert secret is not None
    apply_decision(state, secret.options[0])
    final_strike = pending_decision(state)
    assert final_strike is not None
    apply_decision(state, final_strike.options[0])
    intercept = pending_decision(state)
    assert intercept is not None

    apply_decision(state, intercept.options[-1])
    decision = pending_decision(state)

    assert decision is not None
    assert decision.agent_id == "player_0"
    assert decision.decision_type is DecisionType.MODIFY_DETERRENT
