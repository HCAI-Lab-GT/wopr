"""Strict Concordia failure payload tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.agent import ConcordiaDecisionAgent, ScriptedConcordiaClient
from nuclear_war_concordia.failure import ConcordiaDecisionFailure
from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
)


def test_concordia_agent_invalid_output_raises_failure_snapshot() -> None:
    options = [
        build_action("player_0", ActionType.DRAW, "Draw"),
        build_action("player_0", ActionType.PASS, "Pass"),
    ]
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=ScriptedConcordiaClient(["not-json", "still-not-json"]),
        max_retries=1,
    )

    with pytest.raises(ConcordiaDecisionFailure) as exc_info:
        agent.choose(_observation(options), options)

    snapshot = exc_info.value.snapshot
    assert snapshot["player_id"] == "player_0"
    assert snapshot["turn"] == 1
    assert snapshot["decision_type"] == "pass"
    assert snapshot["raw_visible_responses"] == ["not-json", "still-not-json"]
    assert snapshot["validation_errors"] == ["No action_id parsed"] * 2
    assert snapshot["legal_options"][0]["action_id"] == "player_0:draw"


def _observation(options):
    return Observation(
        player_id="player_0",
        ruleset="table",
        turn=1,
        peace=True,
        self=PrivatePlayerObservation(
            population=20,
            hand=["card-a"],
            secrets=[],
            deterrents=[None, None],
            face_up=None,
            face_down_queue=[None, None],
            final_strike_cards=[],
            pending_orders={},
            alive=True,
            at_war=False,
        ),
        players={},
        draw_count=10,
        discard_count=0,
        decision=DecisionObservation(
            agent_id="player_0",
            decision_type=DecisionType.PASS,
            options=options,
        ),
    )
