"""Unit tests for the live LLM endpoint preflight (no network)."""

from __future__ import annotations

import json

import pytest

from nuclear_war_agents import HTTPResponse
from nuclear_war_env.llm_preflight import run_llm_preflight

FAKE_KEY = "sk-preflight-secret"


def _no_press_payload() -> dict:
    return {
        "players": 4,
        "seed_start": 101,
        "runs": 1,
        "max_turns": 5,
        "seats": {
            "player_0": {
                "agent": "llm_http",
                "client": {
                    "base_url_env": "WOPR_LLM_BASE_URL",
                    "model_env": "WOPR_LLM_MODEL",
                    "api_key_env": "TOGETHER_API_KEY",
                    "provider_label": "together",
                },
            },
            "player_1": {"agent": "random"},
            "player_2": {"agent": "heuristic"},
            "player_3": {"agent": "decision_heuristic"},
        },
    }


def _concordia_payload() -> dict:
    identity = {"name": "Commander 0"}
    client = {
        "base_url_env": "WOPR_LLM_BASE_URL",
        "model_env": "WOPR_LLM_MODEL",
        "api_key_env": "TOGETHER_API_KEY",
        "provider_label": "together",
    }
    return {
        "players": 4,
        "seed": 7,
        "seats": {
            f"player_{index}": {
                "agent": "concordia_http",
                "identity": dict(identity),
                "client": dict(client),
            }
            for index in range(4)
        },
    }


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOPR_LLM_BASE_URL", "https://api.example.test/v1")
    monkeypatch.setenv("WOPR_LLM_MODEL", "example/model-1")
    monkeypatch.setenv("TOGETHER_API_KEY", FAKE_KEY)


def _ok_transport(url, headers, body, timeout_seconds):
    payload = {
        "choices": [{"message": {"content": '{"action_id": "preflight:ok"}'}}],
        "usage": {"prompt_tokens": 21, "completion_tokens": 9},
    }
    return HTTPResponse(200, json.dumps(payload))


def test_preflight_success_reports_endpoint_model_latency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)

    report = run_llm_preflight(_no_press_payload(), transport=_ok_transport)

    assert report["ok"] is True
    assert report["config_kind"] == "no_press_llm_http"
    assert report["seat"] == "player_0"
    assert report["endpoint"] == "https://api.example.test/v1/chat/completions"
    assert report["model"] == "example/model-1"
    assert report["provider_label"] == "together"
    assert isinstance(report["latency_ms"], int)
    assert report["response_snippet_chars"] == len('{"action_id": "preflight:ok"}')


def test_preflight_never_reports_the_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)

    report = run_llm_preflight(_no_press_payload(), transport=_ok_transport)

    assert FAKE_KEY not in json.dumps(report)


def test_preflight_resolves_concordia_http_configs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)

    report = run_llm_preflight(_concordia_payload(), transport=_ok_transport)

    assert report["ok"] is True
    assert report["config_kind"] == "concordia"
    assert report["seat"] == "player_0"


def test_preflight_http_error_raises_clear_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)

    def failing_transport(url, headers, body, timeout_seconds):
        return HTTPResponse(500, "upstream exploded")

    with pytest.raises(ValueError, match="LLM preflight request failed"):
        run_llm_preflight(_no_press_payload(), transport=failing_transport)


def test_preflight_missing_env_var_raises_clear_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)
    monkeypatch.delenv("WOPR_LLM_BASE_URL")

    with pytest.raises(ValueError, match="WOPR_LLM_BASE_URL"):
        run_llm_preflight(_no_press_payload(), transport=_ok_transport)


def test_preflight_missing_api_key_env_raises_clear_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)
    monkeypatch.delenv("TOGETHER_API_KEY")

    with pytest.raises(ValueError, match="TOGETHER_API_KEY"):
        run_llm_preflight(_no_press_payload(), transport=_ok_transport)


def test_preflight_rejects_configs_without_http_seats() -> None:
    payload = _no_press_payload()
    payload["seats"]["player_0"] = {"agent": "llm_first_legal"}

    with pytest.raises(ValueError, match="no HTTP-client seat"):
        run_llm_preflight(payload, transport=_ok_transport)


def test_preflight_rejects_unparseable_configs() -> None:
    with pytest.raises(ValueError, match="not a recognized"):
        run_llm_preflight({"nonsense": True}, transport=_ok_transport)


def test_cli_llm_preflight_exits_nonzero_without_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Env resolution fails before any network I/O, so this is offline-safe.
    monkeypatch.delenv("WOPR_LLM_BASE_URL", raising=False)
    config_path = tmp_path / "pilot.json"
    config_path.write_text(json.dumps(_no_press_payload()), encoding="utf-8")

    from nuclear_war_env.cli import main

    code = main(["llm-preflight", "--config", str(config_path)])

    assert code == 2
    assert "WOPR_LLM_BASE_URL" in capsys.readouterr().err
