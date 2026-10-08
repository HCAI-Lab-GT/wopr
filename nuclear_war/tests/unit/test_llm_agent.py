"""LLM decision agent contract tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_agents import (
    LLMCompletion,
    LLMDecisionAgent,
    ScriptedLLMClient,
    TraceRecorder,
    parse_llm_response,
    render_llm_prompt,
)
from nuclear_war_env.action_models import ActionType, LegalAction, build_action
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
    PublicPlayerObservation,
)


def test_render_llm_prompt_includes_observation_and_legal_options() -> None:
    options = _options()
    prompt = render_llm_prompt(_observation(options), options)

    assert "player_id: p1" in prompt
    assert "decision_type: launch_target" in prompt
    assert options[1].action_id in prompt
    assert "Respond with exactly one legal action_id" in prompt


def test_parse_llm_response_reads_json_action_and_rationale() -> None:
    parsed = parse_llm_response(
        '{"action_id": "p1:pass", "rationale": "conserve cards"}'
    )

    assert parsed.action_id == "p1:pass"
    assert parsed.rationale == "conserve cards"


def test_llm_agent_retries_invalid_output_and_records_trace() -> None:
    options = _options()
    recorder = TraceRecorder()
    agent = LLMDecisionAgent(
        ScriptedLLMClient(["not legal", _response(options[1].action_id)]),
        recorder=recorder,
        max_retries=1,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert recorder.traces[0].selected_action_id == options[1].action_id
    assert recorder.traces[0].retries == 1
    assert recorder.traces[0].to_payload()["rendered_observation"]["player_id"] == "p1"
    assert recorder.traces[0].validation_errors == ["No legal action_id parsed"]


def test_llm_agent_records_provider_metadata_when_client_returns_it() -> None:
    options = _options()
    recorder = TraceRecorder()
    completion = LLMCompletion(_response(options[1].action_id), 17, 0.004)
    agent = LLMDecisionAgent(
        ScriptedLLMClient([completion]),
        recorder=recorder,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert recorder.traces[0].raw_response == _response(options[1].action_id)
    assert recorder.traces[0].provider_latency_ms == 17
    assert recorder.traces[0].provider_cost == 0.004


def test_llm_agent_records_transport_internal_retries() -> None:
    options = _options()
    recorder = TraceRecorder()
    completion = LLMCompletion(
        _response(options[1].action_id), provider_transport_retries=3
    )
    agent = LLMDecisionAgent(ScriptedLLMClient([completion]), recorder=recorder)

    agent.choose(_observation(options), options)

    assert recorder.traces[0].recoverable_provider_retries == 3


def test_llm_agent_falls_back_after_retry_budget() -> None:
    options = _options()
    recorder = TraceRecorder()
    agent = LLMDecisionAgent(
        ScriptedLLMClient(["bad", "still bad"]),
        recorder=recorder,
        fallback="first",
        max_retries=1,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert recorder.traces[0].selected_action_id == options[0].action_id
    assert recorder.traces[0].validation_errors == [
        "No legal action_id parsed",
        "No legal action_id parsed",
    ]
    assert recorder.traces[0].fallback_used is True
    assert recorder.traces[0].to_payload()["fallback_used"] is True


def test_llm_agent_marks_model_chosen_action_as_not_fallback() -> None:
    options = _options()
    recorder = TraceRecorder()
    agent = LLMDecisionAgent(
        ScriptedLLMClient([_response(options[1].action_id)]),
        recorder=recorder,
    )

    agent.choose(_observation(options), options)

    assert recorder.traces[0].fallback_used is False


def test_llm_agent_fallback_pass_selects_pass_option() -> None:
    # The pass-type option is deliberately not options[0], so a passing test proves
    # the "pass" policy chose the pass option rather than merely the first option.
    options = [
        build_action("p1", ActionType.TARGET, "Target p3", {"target": "p3"}),
        build_action("p1", ActionType.PASS, "Pass"),
    ]
    recorder = TraceRecorder()
    agent = LLMDecisionAgent(
        ScriptedLLMClient(["bad"]),
        recorder=recorder,
        fallback="pass",
        max_retries=0,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert selected.action_type is ActionType.PASS
    assert recorder.traces[0].selected_action_id == options[1].action_id


def test_llm_agent_fallback_pass_without_pass_option_uses_first() -> None:
    # No pass-type option exists; the "pass" policy must degrade to options[0]
    # rather than raising a false "Unknown LLM fallback policy" error.
    options = [
        build_action("p1", ActionType.TARGET, "Target p2", {"target": "p2"}),
        build_action("p1", ActionType.TARGET, "Target p3", {"target": "p3"}),
    ]
    recorder = TraceRecorder()
    agent = LLMDecisionAgent(
        ScriptedLLMClient(["bad"]),
        recorder=recorder,
        fallback="pass",
        max_retries=0,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert recorder.traces[0].selected_action_id == options[0].action_id


def test_llm_agent_fallback_unknown_policy_raises_truthful_error() -> None:
    options = _options()
    agent = LLMDecisionAgent(
        ScriptedLLMClient(["bad"]),
        fallback="banana",
        max_retries=0,
    )

    with pytest.raises(ValueError, match="Unknown LLM fallback policy: banana"):
        agent.choose(_observation(options), options)


def _options() -> list[LegalAction]:
    return [
        build_action("p1", ActionType.PASS, "Pass"),
        build_action("p1", ActionType.TARGET, "Target p3", {"target": "p3"}),
    ]


def _response(action_id: str) -> str:
    return json.dumps({"action_id": action_id})


def _observation(options: list[LegalAction]) -> Observation:
    return Observation(
        player_id="p1",
        ruleset="table",
        turn=1,
        peace=False,
        self=PrivatePlayerObservation(
            population=20,
            hand=["missile_1"],
            secrets=[],
            deterrents=[None, None],
            face_up=None,
            face_down_queue=[None, None],
            final_strike_cards=[],
            pending_orders={},
            alive=True,
            at_war=False,
        ),
        players={"p2": _public_player(10), "p3": _public_player(30)},
        draw_count=12,
        discard_count=0,
        decision=DecisionObservation(
            agent_id="p1",
            decision_type=DecisionType.LAUNCH_TARGET,
            options=options,
        ),
    )


def _public_player(population: int) -> PublicPlayerObservation:
    return PublicPlayerObservation(
        population=population,
        hand_count=2,
        secret_count=1,
        deterrent_count=0,
        face_up=None,
        face_down_count=0,
        alive=True,
        at_war=False,
    )
