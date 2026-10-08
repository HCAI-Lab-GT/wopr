"""HTTP-backed Concordia choice model tests."""

from __future__ import annotations

from typing import Any, cast

import pytest

from nuclear_war_agents import LLMCompletion
from nuclear_war_concordia.native_http_model import ConcordiaHTTPChoiceModel

_RESPONSES = ["a", "b"]


def test_sample_choice_accepts_real_action_id_json() -> None:
    model = _model('{"action_id": "player_0:pass"}')

    index, choice, info = model.sample_choice(_choice_document(), _RESPONSES)

    assert (index, choice) == (1, "b")
    assert info["provider_label"] == "test-provider"


def test_sample_choice_accepts_bare_action_id() -> None:
    model = _model("player_0:draw")

    index, choice, _ = model.sample_choice(_choice_document(), _RESPONSES)

    assert (index, choice) == (0, "a")


def test_sample_choice_accepts_bare_letter() -> None:
    model = _model("b")

    index, choice, _ = model.sample_choice(_choice_document(), _RESPONSES)

    assert (index, choice) == (1, "b")


def test_sample_choice_accepts_letter_in_action_id_json() -> None:
    model = _model('{"action_id": "a"}')

    index, choice, _ = model.sample_choice(_choice_document(), _RESPONSES)

    assert (index, choice) == (0, "a")


def test_sample_choice_prompt_lists_real_action_ids() -> None:
    client = FakeHttpClient('{"action_id": "player_0:draw"}')
    model = ConcordiaHTTPChoiceModel(client=cast(Any, client))

    model.sample_choice(_choice_document(), _RESPONSES)

    assert len(client.prompts) == 1
    prompt = client.prompts[0]
    # Once in the lettered option lines, once in the response instruction.
    assert prompt.count("player_0:draw") >= 2
    assert '{"action_id"' in prompt


def test_sample_choice_rejects_prompt_without_scene_payload() -> None:
    client = FakeHttpClient("a")
    model = ConcordiaHTTPChoiceModel(client=cast(Any, client))
    blind_prompt = "\n".join(
        [
            "",
            "Question: Choose one legal WOPR action_id.",
            "  (a) player_0:draw",
            "  (b) player_0:pass",
            "Answer: (",
        ]
    )

    with pytest.raises(ValueError, match="scene payload"):
        model.sample_choice(blind_prompt, _RESPONSES)

    assert client.prompts == []  # guard fires before any provider call


def test_sample_choice_rejects_unknown_action_id() -> None:
    completion = LLMCompletion(raw_response='{"action_id": "player_9:bogus"}')
    model = ConcordiaHTTPChoiceModel(client=cast(Any, FakeHttpClient(completion)))

    with pytest.raises(Exception, match="no choice") as excinfo:
        model.sample_choice(_choice_document(), _RESPONSES)

    assert excinfo.value.__dict__["completion"] is completion
    assert model.last_completion is completion


def _choice_document() -> str:
    return "\n".join(
        [
            "Scene JSON:",
            '{"player_id": "player_0"}',
            "",
            "Question: Choose one legal WOPR action_id.",
            "  (a) player_0:draw",
            "  (b) player_0:pass",
            "Answer: (",
        ]
    )


def _model(raw_response: str) -> ConcordiaHTTPChoiceModel:
    return ConcordiaHTTPChoiceModel(client=cast(Any, FakeHttpClient(raw_response)))


class FakeHttpClient:
    def __init__(self, response: str | LLMCompletion) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> LLMCompletion:
        self.prompts.append(prompt)
        if isinstance(self.response, LLMCompletion):
            return self.response
        return LLMCompletion(
            raw_response=self.response,
            provider_label="test-provider",
        )
