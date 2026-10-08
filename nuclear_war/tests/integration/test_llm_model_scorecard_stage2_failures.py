"""Stage 2 calibration runner failure-path tests."""

from __future__ import annotations

from nuclear_war_agents import LLMCompletion, LLMHttpError
from nuclear_war_agents.llm_fake_clients import FirstLegalLLMClient
from nuclear_war_env import llm_model_scorecard_stage2 as scorecard
from nuclear_war_env.llm_model_scorecard_stage2 import Stage2Config, run_stage2_model


class PromptClient:
    def __init__(self, smoke='{"action_id": "smoke:test"}', game=None, http=False):
        self.smoke_response = smoke
        self.game_response = game
        self.raise_http = http
        self._game_index = 0

    def complete(self, prompt: str) -> LLMCompletion:
        if self.raise_http:
            raise LLMHttpError("LLM HTTP request failed with 500")
        if prompt.startswith("Respond only with this JSON:"):
            return LLMCompletion(
                self.smoke_response,
                provider_latency_ms=4,
                provider_usage={
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            )
        return LLMCompletion(
            self._game_response(prompt),
            provider_latency_ms=5,
            provider_usage={
                "prompt_tokens": 4,
                "completion_tokens": 2,
                "total_tokens": 6,
            },
        )

    def _game_response(self, prompt: str) -> str:
        response = self.game_response
        if response is None:
            return FirstLegalLLMClient().complete(prompt)
        if isinstance(response, tuple):
            response = response[min(self._game_index, len(response) - 1)]
            self._game_index += 1
        if response == "first_legal":
            return FirstLegalLLMClient().complete(prompt)
        return response


def test_stage2_direct_smoke_failures() -> None:
    for expected_error, client in [
        ("empty_final_content", PromptClient(smoke="")),
        ("parse_failure", PromptClient(smoke="{}")),
        ("http_error", PromptClient(http=True)),
    ]:
        failure = run_stage2_model(
            Stage2Config(),
            "demo/model",
            lambda _id, client=client: client,
        )
        assert failure.status == "failed"
        assert (failure.direct_smoke_passed, failure.wopr_one_turn_passed) == (
            False,
            False,
        )
        assert failure.error_type == expected_error
        if expected_error == "http_error":
            assert "500" in (failure.error_message or "")


def test_stage2_trace_validation_error(monkeypatch) -> None:
    monkeypatch.setattr(
        scorecard,
        "_run_wopr_one_turn",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError("Trace artifact fields are invalid")
        ),
    )
    result = run_stage2_model(
        Stage2Config(),
        "demo/model",
        lambda _id: PromptClient(),
    )
    assert (result.status, result.direct_smoke_passed, result.wopr_one_turn_passed) == (
        "failed",
        True,
        False,
    )
    assert result.error_type == "trace_validation_error"


def test_stage2_exhausted_illegal_actions_fail() -> None:
    result = run_stage2_model(
        Stage2Config(max_retries=1),
        "demo/model",
        lambda _id: PromptClient(game='{"action_id":"bogus"}'),
    )
    assert result.status == "failed"
    assert result.wopr_one_turn_passed is False
    assert result.invalid_action_count > 0
    assert result.retry_count > 0
    assert result.error_type == "parse_failure"
