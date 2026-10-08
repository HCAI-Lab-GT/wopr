"""Non-billable HTTP-shaped C2 and full-press composition coverage."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, cast

import pytest

from nuclear_war_agents.llm_http_transport import HTTPResponse
from nuclear_war_concordia.agent import FirstLegalConcordiaClient
from nuclear_war_concordia.c2_artifacts import validate_c2_artifact
from nuclear_war_concordia.call_budget import ChannelCallBudget
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_concordia.press_artifacts import validate_press_artifact
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact


def test_http_authority_members_compose_with_full_press_without_network(
    authority_config_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients: list[FakeHTTPClient] = []

    class FakeHTTPClient:
        def __init__(self, config: object) -> None:
            del config
            clients.append(self)

        def complete(self, scene_text: str) -> str:
            if '"decision_type": "press"' in scene_text:
                return json.dumps(
                    {
                        "action_id": "speak",
                        "message": "The channel is open.",
                        "rationale": "Test message",
                    }
                )
            return FirstLegalConcordiaClient().complete(scene_text)

    monkeypatch.setattr(
        "nuclear_war_concordia.harness_agents.LLMHttpClient", FakeHTTPClient
    )
    payload = _http_authority_payload(authority_config_payload)
    result = run_concordia_no_press_game(load_concordia_no_press_config(payload))

    validate_trace_artifact(result["trace_artifact"], result["replay"])
    c2 = result["c2_artifact"]
    press = result["press_artifact"]
    assert len(clients) == 3
    assert len({id(client) for client in clients}) == 3
    assert c2["deliberations"]
    assert all(len(item["members"]) == 3 for item in c2["deliberations"])
    assert press["messages"]
    assert any(message["speaker"] == "player_0" for message in press["messages"])
    assert result["summary"]["channel_metrics"]["c2"]["call_count"] > 0
    assert result["summary"]["channel_metrics"]["press"]["call_count"] > 0


def test_actual_http_client_composes_with_full_press_and_budget_guard(
    authority_config_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[dict[str, Any]] = []
    decision_types: list[str] = []

    def transport(
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        del url, headers, timeout_seconds
        request = json.loads(body)
        requests.append(request)
        prompt = request["messages"][0]["content"]
        scene_text = prompt.split("Scene JSON:\n", 1)[1].split("\n\nRespond", 1)[0]
        scene = json.loads(scene_text)
        decision_types.append(scene["decision_type"])
        if scene["decision_type"] == "press":
            content = {"action_id": "speak", "message": "Injected transport"}
        else:
            content = {
                "action_id": scene["legal_options"][0]["action_id"],
                "rationale": "first legal through HTTP client",
            }
        return HTTPResponse(
            200,
            json.dumps(
                {
                    "choices": [{"message": {"content": json.dumps(content)}}],
                    "model": request["model"],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                }
            ),
        )

    monkeypatch.setenv("UNUSED_TEST_KEY", "offline-test-key")
    monkeypatch.setattr("nuclear_war_agents.llm_http_client.send_http", transport)
    result = run_concordia_no_press_game(
        load_concordia_no_press_config(
            _http_authority_payload(authority_config_payload)
        ),
        call_budget=ChannelCallBudget(80, 10),
    )

    validate_trace_artifact(result["trace_artifact"], result["replay"])
    validate_c2_artifact(result["c2_artifact"], result["replay"])
    validate_press_artifact(result["press_artifact"], result["replay"])
    assert requests
    assert all(request["model"] == "mock-model" for request in requests)
    assert any(decision_type != "press" for decision_type in decision_types)
    assert "press" in decision_types
    assert result["c2_artifact"]["deliberations"]
    assert all(
        len(item["members"]) == 3 for item in result["c2_artifact"]["deliberations"]
    )
    assert result["press_artifact"]["messages"]
    assert result["summary"]["budget_metrics"]["c2"]["call_count"] <= 80
    assert result["summary"]["budget_metrics"]["press"]["call_count"] <= 10


def _http_authority_payload(
    base_payload: dict[str, object],
) -> dict[str, object]:
    payload = deepcopy(base_payload)
    payload["max_turns"] = 2
    payload["press"] = {"mode": "full_press", "enabled": True, "passes": 1}
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seat = seats["player_0"]
    seat["agent"] = "concordia_http"
    seat["max_retries"] = 0
    seat["client"] = {
        "provider": "together",
        "base_url": "http://mock.invalid/v1",
        "model": "mock-model",
        "api_key_env": "UNUSED_TEST_KEY",
        "provider_label": "test-double",
    }
    return payload
