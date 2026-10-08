"""Native entity per-decision logs must be captured by the client.

Decision traces record the WOPR-rendered scene text, not the model-visible
prompt, so trace inspection could not reveal the 2026-07-01 blind-agent bug.
Capturing EntityAgentWithLogging.get_last_log() per decision puts the true
assembled prompt and each component's contribution into the sidecar.
"""

from __future__ import annotations

import json

import pytest

from nuclear_war_concordia.native import NativeConcordiaEntityClient


def test_native_client_records_entity_log_after_act() -> None:
    pytest.importorskip("concordia")
    from nuclear_war_concordia import native

    client = native.build_native_first_legal_client({"name": "Commander 0"})

    client.complete(_scene_text())

    log = client.last_entity_log
    assert isinstance(log, dict)
    act_prompt = "\n".join(log["__act__"]["Prompt"])
    assert "Scene JSON:" in act_prompt
    json.dumps(log)  # sidecar payloads must be JSON-serializable


def test_native_client_without_entity_log_support_records_none() -> None:
    client = NativeConcordiaEntityClient(
        entity=PlainEntity("player_0:draw"),
        identity={"name": "Commander 0"},
        action_spec_factory=fake_action_spec,
    )

    client.complete(_scene_text())

    assert client.last_entity_log is None


def _scene_text() -> str:
    scene = {
        "player_id": "player_0",
        "decision_type": "pass",
        "legal_options": [
            {"action_id": "player_0:draw", "label": "Draw"},
            {"action_id": "player_0:pass", "label": "Pass"},
        ],
    }
    return f"Scene JSON:\n{json.dumps(scene)}\n\n"


class PlainEntity:
    def __init__(self, choice: str) -> None:
        self.choice = choice

    def observe(self, observation: str) -> None:
        del observation

    def act(self, action_spec):
        del action_spec
        return self.choice


def fake_action_spec(**kwargs):
    return FakeActionSpec(tuple(kwargs["options"]))


class FakeActionSpec:
    def __init__(self, options: tuple[str, ...]) -> None:
        self.options = options
