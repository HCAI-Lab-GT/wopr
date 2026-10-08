# tests/unit/test_decision_types.py
from __future__ import annotations

from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.engine.decision import (
    Decision,
    DecisionCursor,
    DecisionType,
    TurnPhase,
)


def test_decision_carries_agent_options_and_context() -> None:
    option = build_action("player_0", ActionType.ENQUEUE, "Place x", {"cards": ["x"]})
    decision = Decision(
        agent_id="player_0",
        decision_type=DecisionType.PLACE,
        options=[option],
        context={"phase": "place"},
    )
    assert decision.agent_id == "player_0"
    assert decision.decision_type is DecisionType.PLACE
    assert decision.options == [option]
    assert decision.context == {"phase": "place"}


def test_cursor_tracks_player_phase_and_pending() -> None:
    cursor = DecisionCursor(
        turn_player="player_1", phase=TurnPhase.ATTACK, pending=None
    )
    assert cursor.turn_player == "player_1"
    assert cursor.phase is TurnPhase.ATTACK
    assert cursor.pending is None
