"""Native Concordia entity client tests."""

from __future__ import annotations

import json
import types

import pytest

from nuclear_war_concordia.native import NativeConcordiaEntityClient


def test_native_entity_client_uses_choice_action_ids() -> None:
    entity = FakeEntity("player_0:pass")
    client = NativeConcordiaEntityClient(
        entity=entity,
        identity={"name": "Commander 0"},
        action_spec_factory=fake_action_spec,
    )
    scene = {
        "player_id": "player_0",
        "decision_type": "pass",
        "legal_options": [
            {"action_id": "player_0:draw", "label": "Draw"},
            {"action_id": "player_0:pass", "label": "Pass"},
        ],
    }

    raw_response = client.complete(f"Scene JSON:\n{json.dumps(scene)}\n\n")

    assert isinstance(raw_response, str)
    response = json.loads(raw_response)
    assert response["action_id"] == "player_0:pass"
    assert entity.observations == [f"Scene JSON:\n{json.dumps(scene)}\n\n"]
    assert entity.action_spec is not None
    assert entity.action_spec.options == ("player_0:draw", "player_0:pass")


def test_native_first_legal_entity_prompt_contains_scene_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("concordia")
    from nuclear_war_concordia import native

    prompts: list[str] = []
    monkeypatch.setattr(
        native, "_no_language_model_module", lambda: _spy_model_module(prompts)
    )
    client = native.build_native_first_legal_client({"name": "Commander 0"})

    raw_response = client.complete(_scene_text())

    assert prompts, "native entity never reached sample_choice"
    prompt = prompts[0]
    assert "Scene JSON:" in prompt
    assert '"population"' in prompt
    assert '"player_0:draw"' in prompt
    assert isinstance(raw_response, str)
    assert json.loads(raw_response)["action_id"] == "player_0:draw"


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


def _spy_model_module(prompts: list[str]) -> types.SimpleNamespace:
    import importlib

    no_language_model = importlib.import_module(
        "concordia.language_model.no_language_model"
    )

    class SpyModel(no_language_model.NoLanguageModel):
        def sample_choice(self, prompt, responses, *, seed=None):
            del seed
            prompts.append(prompt)
            return 0, responses[0], {}

    return types.SimpleNamespace(NoLanguageModel=SpyModel)


class FakeEntity:
    def __init__(self, choice: str) -> None:
        self.choice = choice
        self.observations: list[str] = []
        self.action_spec = None

    def observe(self, observation: str) -> None:
        self.observations.append(observation)

    def act(self, action_spec):
        self.action_spec = action_spec
        return self.choice


def fake_action_spec(**kwargs):
    return FakeActionSpec(tuple(kwargs["options"]))


class FakeActionSpec:
    def __init__(self, options: tuple[str, ...]) -> None:
        self.options = options
