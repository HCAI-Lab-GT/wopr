from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.decision_loop import (
    _advance,
    _RoundStamper,
    apply_decision,
    pending_decision,
)
from nuclear_war_env.engine.decision import DecisionCursor, DecisionType, TurnPhase
from nuclear_war_env.fallout import FalloutOutcome, SpinnerEffect
from nuclear_war_env.state import GameState
from nuclear_war_env.table_turn import TurnResult


def test_launch_elimination_pauses_for_final_strike_target(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    retaliation_state.players["player_1"].population = [5]
    retaliation_state.players["player_1"].hand = [
        "retaliation_delivery",
        "retaliation_warhead",
    ]
    retaliation_state.players["player_0"].pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["attack_warhead"],
            "target": "player_1",
        }
    }
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.INTERCEPT)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    intercept = pending_decision(retaliation_state)
    assert intercept is not None

    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )

    apply_decision(retaliation_state, intercept.options[-1])
    decision = pending_decision(retaliation_state)

    assert decision is not None
    assert decision.decision_type is DecisionType.FINAL_STRIKE_TARGET
    assert decision.agent_id == "player_1"
    assert decision.options[0].payload == {"target": "player_0"}
