"""Concordia decision agent transient-error recovery (spec failure model).

Spec (docs/specs/2026-06-22-concordia-agent-harness-design.md) marks "provider
timeout or HTTP error" as *recoverable once*, while config faults stay strict.
These tests pin that boundary at the ConcordiaDecisionAgent level.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from nuclear_war_agents import LLMCompletion, LLMConfigError, LLMHttpError
from nuclear_war_concordia.agent import (
    ConcordiaDecisionAgent,
    FirstLegalConcordiaClient,
)
from nuclear_war_concordia.failure import ConcordiaDecisionFailure
from nuclear_war_env.action_models import ActionType, LegalAction, build_action
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
    PublicPlayerObservation,
)


def test_agent_retries_transient_http_error_then_succeeds() -> None:
    options = _options()
    traces: list[dict[str, Any]] = []
    client = _FlakyFirstLegalClient(failures=1, error=LLMHttpError("connection reset"))
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        trace_sink=traces,
        max_retries=1,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert client.calls == 2
    # The transient retry is recorded on its own counter, NOT as a model
    # validation error (which would inflate invalid-action metrics), and the
    # model round-trip retry count stays zero (only one completion happened).
    assert traces[0]["recoverable_provider_retries"] == 1
    assert traces[0]["validation_errors"] == []
    assert traces[0]["retries"] == 0


def test_agent_retries_socket_timeout_then_succeeds() -> None:
    options = _options()
    client = _FlakyFirstLegalClient(failures=1, error=TimeoutError("slow provider"))
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        max_retries=1,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert client.calls == 2


def test_agent_does_not_retry_config_error() -> None:
    options = _options()
    client = _ConfigErrorClient()
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        max_retries=1,
    )

    with pytest.raises(ConcordiaDecisionFailure) as exc_info:
        agent.choose(_observation(options), options)

    assert client.calls == 1  # config faults are fatal: never retried
    assert exc_info.value.snapshot["exception"]["type"] == "LLMConfigError"


def test_agent_fails_after_persistent_transient_errors() -> None:
    options = _options()
    client = _FlakyFirstLegalClient(failures=99, error=LLMHttpError("provider down"))
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        max_retries=1,
    )

    with pytest.raises(ConcordiaDecisionFailure) as exc_info:
        agent.choose(_observation(options), options)

    assert client.calls == 2  # initial attempt + one recoverable retry
    assert exc_info.value.snapshot["exception"]["type"] == "LLMHttpError"
    # A distinct message from parse/legality exhaustion.
    assert "recoverable" in str(exc_info.value).lower()


def test_agent_interleaves_transient_and_illegal_retries_consistently() -> None:
    # transient blip -> illegal model output -> legal: the transport retry lands
    # on recoverable_provider_retries; the illegal output lands on retries and
    # validation_errors; all trace invariants must hold together.
    options = _options()
    traces: list[dict[str, Any]] = []
    client = _SequencedClient(
        [LLMHttpError("blip"), "not-json", _FIRST_LEGAL],
    )
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        trace_sink=traces,
        max_retries=2,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert client.calls == 3
    trace = traces[0]
    assert trace["recoverable_provider_retries"] == 1
    assert trace["retries"] == 1
    assert trace["validation_errors"] == ["No action_id parsed"]
    assert len(trace["prompts"]) == len(trace["raw_responses"]) == 2


def test_agent_reflects_transport_internal_retries_in_trace() -> None:
    # A completion whose HTTP client consumed 429/5xx retries internally must
    # still surface those on recoverable_provider_retries (spec: transport
    # retries stay observable), even though no agent-level retry occurred.
    options = _options()
    traces: list[dict[str, Any]] = []
    completion = LLMCompletion(
        raw_response=json.dumps({"action_id": options[0].action_id}),
        provider_transport_retries=2,
    )
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=_SequencedClient([completion]),
        trace_sink=traces,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    assert traces[0]["recoverable_provider_retries"] == 2


def test_agent_sums_agent_level_and_transport_internal_retries() -> None:
    options = _options()
    traces: list[dict[str, Any]] = []
    legal = LLMCompletion(
        raw_response=json.dumps({"action_id": options[0].action_id}),
        provider_transport_retries=1,
    )
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=_SequencedClient([LLMHttpError("blip"), legal]),
        trace_sink=traces,
        max_retries=1,
    )

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    # one agent-level transient retry + one transport-internal retry
    assert traces[0]["recoverable_provider_retries"] == 2


def test_agent_zero_retries_still_fails_on_transient() -> None:
    options = _options()
    client = _FlakyFirstLegalClient(failures=1, error=LLMHttpError("provider down"))
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        max_retries=0,
    )

    with pytest.raises(ConcordiaDecisionFailure):
        agent.choose(_observation(options), options)

    assert client.calls == 1  # no budget: one attempt only


class _FlakyFirstLegalClient:
    """Raise ``error`` on the first ``failures`` calls, then choose first legal."""

    def __init__(self, *, failures: int, error: Exception) -> None:
        self._failures = failures
        self._error = error
        self._inner = FirstLegalConcordiaClient()
        self.calls = 0

    def complete(self, scene_text: str) -> str:
        self.calls += 1
        if self.calls <= self._failures:
            raise self._error
        return self._inner.complete(scene_text)


class _ConfigErrorClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, scene_text: str) -> str:
        del scene_text
        self.calls += 1
        raise LLMConfigError("LLM HTTP client requires base_url")


_FIRST_LEGAL = object()


class _SequencedClient:
    """Play a scripted sequence: Exceptions are raised, strings are returned
    verbatim, and the _FIRST_LEGAL sentinel delegates to first-legal choice."""

    def __init__(self, steps: list[object]) -> None:
        self._steps = steps
        self._inner = FirstLegalConcordiaClient()
        self.calls = 0

    def complete(self, scene_text: str) -> str | LLMCompletion:
        step = self._steps[self.calls]
        self.calls += 1
        if isinstance(step, Exception):
            raise step
        if step is _FIRST_LEGAL:
            return self._inner.complete(scene_text)
        if isinstance(step, LLMCompletion):
            return step
        assert isinstance(step, str)
        return step


def _options() -> list[LegalAction]:
    return [
        build_action("player_0", ActionType.DRAW, "Draw"),
        build_action("player_0", ActionType.PASS, "Pass"),
    ]


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
