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


def _final_order() -> dict[str, object]:
    return {
        "delivery": "retaliation_delivery",
        "warheads": ["retaliation_warhead"],
        "target": None,
        "eliminated_by": "player_0",
    }


def _no_radiation(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )


def test_final_strike_pending_order_surfaces_target_decision(
    retaliation_state: GameState,
) -> None:
    player = retaliation_state.players["player_1"]
    player.alive = False
    player.population = []
    player.pending_orders["final_strike"] = [_final_order()]
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)

    _advance(retaliation_state, _RoundStamper(TurnResult()), True)

    decision = pending_decision(retaliation_state)
    assert decision is not None
    assert decision.decision_type is DecisionType.FINAL_STRIKE_TARGET
    assert decision.agent_id == "player_1"
    assert decision.options[0].payload == {"target": "player_0"}


def test_targeted_final_strike_runs_without_target_decision(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    player = retaliation_state.players["player_1"]
    player.alive = False
    player.population = []
    player.pending_orders["final_strike"] = [{**_final_order(), "target": "player_2"}]
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)
    stamper = _RoundStamper(TurnResult())
    _no_radiation(monkeypatch)

    _advance(retaliation_state, stamper, True)

    decision = pending_decision(retaliation_state)
    assert (
        decision is None
        or decision.decision_type is not DecisionType.FINAL_STRIKE_TARGET
    )
    assert not player.pending_orders.get("final_strike")
    assert [event.event_type for event in stamper.result.events] == [
        "final_strike_executed"
    ]
    assert decision is not None
    assert decision.decision_type is DecisionType.INTERCEPT


def test_untargetable_final_strike_is_cleared_without_decision(
    retaliation_state: GameState,
) -> None:
    player = retaliation_state.players["player_1"]
    player.alive = False
    player.population = []
    for target_id in ("player_0", "player_2"):
        retaliation_state.players[target_id].alive = False
        retaliation_state.players[target_id].population = []
    player.pending_orders["final_strike"] = [_final_order()]
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)
    stamper = _RoundStamper(TurnResult())

    _advance(retaliation_state, stamper, True)

    assert pending_decision(retaliation_state) is None
    assert not player.pending_orders.get("final_strike")
    assert [event.event_type for event in stamper.result.events] == [
        "final_strike_executed"
    ]


def test_applying_final_strike_target_runs_queued_final_strike(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    player = retaliation_state.players["player_1"]
    player.alive = False
    player.population = []
    player.pending_orders["final_strike"] = [_final_order()]
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    decision = pending_decision(retaliation_state)
    assert decision is not None
    _no_radiation(monkeypatch)

    events = apply_decision(retaliation_state, decision.options[0])

    assert any(event.event_type == "final_strike_targeted" for event in events)
    assert any(event.event_type == "final_strike_executed" for event in events)
    assert not player.pending_orders.get("final_strike")
