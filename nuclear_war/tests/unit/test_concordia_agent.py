"""Concordia decision agent contract tests."""

from __future__ import annotations

import json
from typing import Any

import pytest

from nuclear_war_concordia.agent import (
    ConcordiaDecisionAgent,
    FirstLegalConcordiaClient,
    ScriptedConcordiaClient,
)
from nuclear_war_env.action_models import ActionType, LegalAction, build_action
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
    PublicPlayerObservation,
)


def test_concordia_agent_selects_legal_action_and_records_trace() -> None:
    options = _options()
    traces: list[dict[str, Any]] = []
    identity = {"name": "Analyst Zero", "role": "cautious commander"}
    agent = ConcordiaDecisionAgent(
        identity=identity,
        client=ScriptedConcordiaClient([_response(options[1].action_id)]),
        trace_sink=traces,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert traces[0]["selected_action_id"] == options[1].action_id
    assert (
        traces[0]["rendered_observation"]["concordia"]["identity"]["name"]
        == (identity["name"])
    )
    assert traces[0]["retries"] == 0
    assert traces[0]["validation_errors"] == []


def test_concordia_agent_fails_after_invalid_retry() -> None:
    options = _options()
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=ScriptedConcordiaClient(["not-json", "still-not-json"]),
        max_retries=1,
    )

    with pytest.raises(ValueError, match="No legal Concordia action selected"):
        agent.choose(_observation(options), options)


def test_concordia_agent_recovers_verbatim_legal_action_from_prose() -> None:
    options = _options()
    traces: list[dict[str, Any]] = []
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=ScriptedConcordiaClient(
            [f"I choose {options[1].action_id} because passing is legal."]
        ),
        trace_sink=traces,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert traces[0]["selected_action_id"] == options[1].action_id


def test_first_legal_concordia_client_selects_first_legal_option() -> None:
    options = _options()
    traces: list[dict[str, Any]] = []
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=FirstLegalConcordiaClient(),
        trace_sink=traces,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert traces[0]["selected_action_id"] == options[0].action_id


def _options() -> list[LegalAction]:
    return [
        build_action("player_0", ActionType.DRAW, "Draw"),
        build_action("player_0", ActionType.PASS, "Pass"),
    ]


def _response(action_id: str) -> str:
    return json.dumps({"action_id": action_id, "rationale": "selected legal action"})


def _observation(options: list[LegalAction]) -> Observation:
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
        players={"player_1": _public_player(30)},
        draw_count=10,
        discard_count=0,
        decision=DecisionObservation(
            agent_id="player_0",
            decision_type=DecisionType.PASS,
            options=options,
        ),
    )


def _public_player(population: int) -> PublicPlayerObservation:
    return PublicPlayerObservation(
        population=population,
        hand_count=3,
        secret_count=0,
        deterrent_count=0,
        face_up=None,
        face_down_count=2,
        alive=True,
        at_war=False,
    )
