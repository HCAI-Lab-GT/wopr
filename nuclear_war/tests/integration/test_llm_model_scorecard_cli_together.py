"""CLI tests for Together-backed model scorecard Stage 2."""

from __future__ import annotations

import json

from nuclear_war_agents import HTTPResponse, LLMHttpClient
from nuclear_war_env import llm_model_scorecard_cli as scorecard_cli
from nuclear_war_env.cli import main
from nuclear_war_env.llm_model_scorecard_stage2_support import Stage2ModelResult


def test_cli_stage2_together_builds_provider_client_without_network(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"
    seen: dict[str, object] = {}
    requests: list[dict[str, object]] = []

    def fake_run_stage2_model(config, model_id, client_factory):
        client = client_factory(model_id)
        seen["config"] = config
        seen["model_id"] = model_id
        seen["client"] = client
        return Stage2ModelResult(
            model_id=model_id,
            status="passed",
            direct_smoke_passed=True,
            wopr_one_turn_passed=True,
            trace_count=0,
            invalid_action_count=0,
            retry_count=0,
            selected_action_ids=(),
            provider_usage=None,
            provider_latency_ms=None,
            error_type=None,
            error_message=None,
        )

    monkeypatch.setattr(scorecard_cli, "run_stage2_model", fake_run_stage2_model)
    monkeypatch.setenv("TOGETHER_API_KEY", "secret-token")

    code = main(
        _args(catalog_path, out_dir)
        + [
            "--provider",
            "together",
            "--model-limit",
            "1",
            "--max-models-cost-usd",
            "0.50",
            "--max-tokens",
            "37",
            "--reasoning-effort",
            "low",
        ]
    )

    client = seen["client"]
    assert isinstance(client, LLMHttpClient)
    http_client = LLMHttpClient(
        client.config,
        transport=lambda url, headers, body, timeout: _record_request(
            requests, url, headers, body, timeout
        ),
        monotonic_ms=lambda: 1,
    )
    completion = http_client.complete("Prompt text")
    captured = capsys.readouterr()
    assert code == 0
    assert client.config.provider == "together"
    assert client.config.model == "demo/low-cost"
    assert client.config.max_tokens == 37
    assert client.config.reasoning_effort == "low"
    assert seen["model_id"] == "demo/low-cost"
    assert completion.raw_response == '{"action_id": "smoke:test"}'
    assert completion.provider_label == "together"
    assert completion.provider_model == "demo/low-cost"
    assert requests == [
        {
            "url": "https://api.together.ai/v1/chat/completions",
            "authorization": "Bearer secret-token",
            "timeout": 60,
            "body": {
                "model": "demo/low-cost",
                "messages": [{"role": "user", "content": "Prompt text"}],
                "temperature": 0.0,
                "max_tokens": 37,
                "reasoning_effort": "low",
            },
        }
    ]
    assert json.loads(captured.out)


def _write_catalog(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(_catalog_payload()), encoding="utf-8")
    return catalog_path


def _args(catalog_path, out_dir) -> list[str]:
    return [
        "llm-model-scorecard",
        "--catalog",
        str(catalog_path),
        "--out",
        str(out_dir),
        "--stage",
        "stage2",
    ]


def _catalog_payload() -> dict[str, object]:
    return {"chat": [{"id": "demo/low-cost", "name": "Low Cost"}]}


def _record_request(
    requests: list[dict[str, object]],
    url: str,
    headers: dict[str, str],
    body: bytes,
    timeout: int,
) -> HTTPResponse:
    requests.append(
        {
            "url": url,
            "authorization": headers["Authorization"],
            "timeout": timeout,
            "body": json.loads(body.decode("utf-8")),
        }
    )
    response = {"choices": [{"message": {"content": '{"action_id": "smoke:test"}'}}]}
    return HTTPResponse(200, json.dumps(response))
