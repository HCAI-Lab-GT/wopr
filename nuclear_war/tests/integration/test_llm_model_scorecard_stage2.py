"""Stage 2 calibration runner success-path tests."""

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


def test_stage2_success_aggregates_smoke_usage() -> None:
    result = run_stage2_model(Stage2Config(), "demo/model", lambda _id: PromptClient())
    assert (result.status, result.direct_smoke_passed, result.wopr_one_turn_passed) == (
        "passed",
        True,
        True,
    )
    assert (result.trace_count, result.invalid_action_count, result.retry_count) == (
        5,
        0,
        0,
    )
    assert result.selected_action_ids[0].startswith("player_0:setup_place:")
    assert result.selected_action_ids[1].startswith("player_0:setup_place:")
    assert result.selected_action_ids[2].startswith("player_0:secret_target")
    assert result.selected_action_ids[3] == "player_0:modify_deterrent"
    assert result.selected_action_ids[4].startswith("player_0:enqueue:")
    assert (result.provider_usage, result.provider_latency_ms) == (
        {"prompt_tokens": 21, "completion_tokens": 11, "total_tokens": 32},
        29,
    )
    assert (result.error_type, result.error_message) == (None, None)


def test_stage2_recovered_retry_records_counts() -> None:
    result = run_stage2_model(
        Stage2Config(max_retries=1),
        "demo/model",
        lambda _id: PromptClient(game=("{}", "first_legal")),
    )
    assert (result.status, result.direct_smoke_passed, result.wopr_one_turn_passed) == (
        "passed",
        True,
        True,
    )
    assert (result.trace_count, result.invalid_action_count, result.retry_count) == (
        5,
        1,
        1,
    )
    assert (result.provider_usage, result.provider_latency_ms) == (
        {"prompt_tokens": 25, "completion_tokens": 13, "total_tokens": 38},
        34,
    )


def test_stage2_uses_harness_client_override(monkeypatch) -> None:
    captured = {}

    def fake_run_no_press_llm_game(config):
        captured["config"] = config
        return {
            "replay": {"winner": None},
            "trace_artifact": {
                "traces": [
                    {
                        "selected_action_id": "demo:action",
                        "raw_response": '{"action_id": "demo:action"}',
                        "parse_result": {"action_id": "demo:action", "rationale": None},
                        "validation_errors": [],
                        "retries": 0,
                        "provider_usage": None,
                        "provider_latency_ms": None,
                    }
                ]
            },
        }

    monkeypatch.setattr(scorecard, "run_no_press_llm_game", fake_run_no_press_llm_game)
    result = run_stage2_model(Stage2Config(), "demo/model", lambda _id: PromptClient())
    assert (result.direct_smoke_passed, result.wopr_one_turn_passed) == (True, True)
    assert captured["config"].seats["player_0"].agent == "llm_http"
    assert captured["config"].seats["player_0"].client_override is not None
