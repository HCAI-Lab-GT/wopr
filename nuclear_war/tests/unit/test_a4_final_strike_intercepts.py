from __future__ import annotations

from final_strike_test_helpers import no_radiation, queue_final_strike
from pytest import MonkeyPatch

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import (
    _advance,
    _RoundStamper,
    apply_decision,
    pending_decision,
)
from nuclear_war_env.engine.decision import DecisionCursor, DecisionType, TurnPhase
from nuclear_war_env.state import GameState
from nuclear_war_env.table_turn import TurnResult


def test_final_strike_target_pauses_for_intercept_before_damage(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    queue_final_strike(retaliation_state)
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    target = pending_decision(retaliation_state)
    assert target is not None
    no_radiation(monkeypatch)

    events = apply_decision(retaliation_state, target.options[0])
    decision = pending_decision(retaliation_state)

    assert [event.event_type for event in events[:2]] == [
        "final_strike_targeted",
        "final_strike_executed",
    ]
    assert not any(event.event_type == "spinner_result" for event in events)
    assert decision is not None
    assert decision.decision_type is DecisionType.INTERCEPT
    assert decision.agent_id == "player_0"


def test_final_strike_launch_can_be_intercepted_by_defender(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    retaliation_state.register_cards(
        [
            Card(
                "am",
                CardCategory.ANTIMISSILE,
                "Anti Missile",
                metadata={"intercept": "any"},
            )
        ]
    )
    retaliation_state.players["player_0"].hand = ["am"]
    queue_final_strike(retaliation_state)
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    target = pending_decision(retaliation_state)
    assert target is not None
    apply_decision(retaliation_state, target.options[0])
    intercept = pending_decision(retaliation_state)
    assert intercept is not None
    no_radiation(monkeypatch)

    events = apply_decision(retaliation_state, intercept.options[0])

    assert [event.event_type for event in events[:1]] == ["intercept_success"]
    assert not any(event.event_type == "warhead_detonated" for event in events)


def test_multiple_final_strike_launches_get_separate_intercept_decisions(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    retaliation_state.register_cards(
        [
            Card(
                "second_delivery",
                CardCategory.DELIVERY,
                "Second",
                metadata={"capacity": 1},
            ),
            Card("second_warhead", CardCategory.WARHEAD, "Second Warhead", value=10),
        ]
    )
    queue_final_strike(retaliation_state)
    retaliation_state.players["player_1"].pending_orders["final_strike"].append(
        {
            "delivery": "second_delivery",
            "warheads": ["second_warhead"],
            "target": None,
            "eliminated_by": "player_0",
        }
    )
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    target = pending_decision(retaliation_state)
    assert target is not None
    apply_decision(retaliation_state, target.options[0])
    first = pending_decision(retaliation_state)
    assert first is not None
    no_radiation(monkeypatch)

    events = apply_decision(retaliation_state, first.options[-1])
    second = pending_decision(retaliation_state)

    assert [event.event_type for event in events].count("spinner_result") == 1
    assert second is not None
    assert second.decision_type is DecisionType.INTERCEPT
    assert second.context["delivery"] == "second_delivery"


def test_dead_pretargeted_final_strike_launch_is_not_requeued(
    retaliation_state: GameState,
) -> None:
    player = retaliation_state.players["player_1"]
    player.alive = False
    player.population = []
    retaliation_state.players["player_2"].alive = False
    retaliation_state.players["player_2"].population = []
    player.pending_orders["final_strike"] = [
        {
            "delivery": "attack_delivery",
            "warheads": ["attack_warhead"],
            "target": "player_2",
            "eliminated_by": "player_0",
        },
        {
            "delivery": "retaliation_delivery",
            "warheads": ["retaliation_warhead"],
            "target": None,
            "eliminated_by": "player_0",
        },
    ]
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    target = pending_decision(retaliation_state)
    assert target is not None

    apply_decision(retaliation_state, target.options[0])

    launches = player.pending_orders.get("launches", {})
    assert "attack_delivery" not in launches
    assert "retaliation_delivery" in launches
    intercept = pending_decision(retaliation_state)
    assert intercept is not None
    assert intercept.context["delivery"] == "retaliation_delivery"
