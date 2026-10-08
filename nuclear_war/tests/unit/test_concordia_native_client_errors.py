"""Native Concordia client error-path and blind-agent guard tests."""

from __future__ import annotations

import json
from typing import Any, cast

import pytest

from nuclear_war_agents import LLMCompletion
from nuclear_war_concordia.native import NativeConcordiaEntityClient


def test_native_client_returns_completion_when_choice_invalid() -> None:
    pytest.importorskip("concordia")
    from concordia.language_model import language_model

    completion = LLMCompletion(raw_response='{"action_id": "player_9:bogus"}')
    model = StubModel(None)
    client = NativeConcordiaEntityClient(
        entity=CompletionThenRaisingEntity(
            language_model.InvalidResponseError("no choice"),
            model,
            completion,
        ),
        identity={"name": "Commander 0"},
        model=cast(Any, model),
        action_spec_factory=fake_action_spec,
    )

    result = client.complete(_scene_text())

    assert isinstance(result, LLMCompletion)
    assert result.raw_response == '{"action_id": "player_9:bogus"}'


def test_native_client_reraises_invalid_choice_without_completion() -> None:
    pytest.importorskip("concordia")
    from concordia.language_model import language_model

    client = NativeConcordiaEntityClient(
        entity=RaisingEntity(language_model.InvalidResponseError("no choice")),
        identity={"name": "Commander 0"},
        model=cast(Any, StubModel(None)),
        action_spec_factory=fake_action_spec,
    )

    with pytest.raises(language_model.InvalidResponseError):
        client.complete(_scene_text())


def test_native_client_reraises_unexpected_entity_errors() -> None:
    completion = LLMCompletion(raw_response="boom payload")
    model = StubModel(None)
    client = NativeConcordiaEntityClient(
        entity=CompletionThenRaisingEntity(RuntimeError("boom"), model, completion),
        identity={"name": "Commander 0"},
        model=cast(Any, model),
        action_spec_factory=fake_action_spec,
    )

    with pytest.raises(RuntimeError) as excinfo:
        client.complete(_scene_text())

    assert excinfo.value.__dict__["completion"] is completion


def test_native_client_does_not_attach_stale_completion_to_new_error() -> None:
    stale = LLMCompletion(raw_response='{"action_id": "player_0:old"}')
    error = RuntimeError("current request failed")
    client = NativeConcordiaEntityClient(
        entity=RaisingEntity(error),
        identity={"name": "Commander 0"},
        model=cast(Any, StubModel(stale)),
        action_spec_factory=fake_action_spec,
    )

    with pytest.raises(RuntimeError) as excinfo:
        client.complete(_scene_text())

    assert not hasattr(excinfo.value, "completion")


def test_blind_native_http_entity_fails_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-enacts the 2026-07-01 blind-agent bug: with no context components,
    the runtime guard must fail the decision instead of letting the seat
    silently choose without game state."""
    pytest.importorskip("concordia")
    from nuclear_war_agents import HTTPClientConfig
    from nuclear_war_concordia import native, native_entity

    monkeypatch.setattr(native_entity, "_context_components", lambda _agent_name: {})
    client = native.build_native_http_client(
        {"name": "Commander 0"},
        HTTPClientConfig(base_url="http://127.0.0.1:9", model="test-model"),
    )

    with pytest.raises(ValueError, match="scene payload"):
        client.complete(_scene_text())


def _scene_text() -> str:
    scene = {
        "player_id": "player_0",
        "decision_type": "pass",
        "observation": {
            "self": {"population": 25},
            "players": {"player_1": {"population": 20}},
        },
        "legal_options": [
            {"action_id": "player_0:draw", "label": "Draw"},
            {"action_id": "player_0:pass", "label": "Pass"},
        ],
    }
    return f"Scene JSON:\n{json.dumps(scene, indent=2)}\n\n"


class RaisingEntity:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def observe(self, observation: str) -> None:
        del observation

    def act(self, action_spec):
        del action_spec
        raise self.error


class CompletionThenRaisingEntity:
    def __init__(
        self,
        error: Exception,
        model: StubModel,
        completion: LLMCompletion,
    ) -> None:
        self.error = error
        self.model = model
        self.completion = completion

    def observe(self, observation: str) -> None:
        del observation

    def act(self, action_spec):
        del action_spec
        self.model.last_completion = self.completion
        raise self.error


class StubModel:
    def __init__(self, last_completion: LLMCompletion | None) -> None:
        self.last_completion = last_completion


def fake_action_spec(**kwargs):
    return FakeActionSpec(tuple(kwargs["options"]))


class FakeActionSpec:
    def __init__(self, options: tuple[str, ...]) -> None:
        self.options = options
