"""ConcordiaDecisionAgent must thread native entity logs into traces."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_concordia.agent import ConcordiaDecisionAgent
from nuclear_war_env.action_models import ActionType, LegalAction
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
)


def test_agent_trace_includes_entity_log_from_native_client() -> None:
    traces: list[dict[str, Any]] = []
    agent = ConcordiaDecisionAgent(
        identity={"name": "Commander 0"},
        client=LoggingStubClient(),
        trace_sink=traces,
    )

    agent.choose(_observation(), _options())

    concordia_payload = traces[0]["rendered_observation"]["concordia"]
    assert concordia_payload["entity_log"] == {"__act__": {"Value": "stub"}}


def test_agent_trace_omits_entity_log_for_plain_clients() -> None:
    traces: list[dict[str, Any]] = []
    agent = ConcordiaDecisionAgent(
        identity={"name": "Commander 0"},
        client=PlainStubClient(),
        trace_sink=traces,
    )

    agent.choose(_observation(), _options())

    assert "entity_log" not in traces[0]["rendered_observation"]["concordia"]


def _observation() -> Observation:
    options = _options()
    return Observation(
        player_id="player_0",
        ruleset="base",
        turn=1,
        peace=True,
        self=PrivatePlayerObservation(
            population=25,
            hand=[],
            secrets=[],
            deterrents=[],
            face_up=None,
            face_down_queue=[],
            final_strike_cards=[],
            pending_orders={},
            alive=True,
            at_war=False,
        ),
        players={},
        draw_count=0,
        discard_count=0,
        decision=DecisionObservation(
            agent_id="player_0",
            decision_type=DecisionType.PASS,
            options=options,
        ),
    )


def _options() -> list[LegalAction]:
    return [
        LegalAction(
            action_id="player_0:draw",
            player_id="player_0",
            action_type=ActionType.DRAW,
            label="Draw",
        )
    ]


class LoggingStubClient:
    last_entity_log = {"__act__": {"Value": "stub"}}

    def complete(self, scene_text: str) -> str:
        del scene_text
        return json.dumps({"action_id": "player_0:draw", "rationale": "stub"})


class PlainStubClient:
    def complete(self, scene_text: str) -> str:
        del scene_text
        return json.dumps({"action_id": "player_0:draw", "rationale": "stub"})
