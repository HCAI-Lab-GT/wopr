from __future__ import annotations

import json
from http.server import ThreadingHTTPServer
from threading import Thread
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from nuclear_war_env.live_api_server import create_live_api_server
from nuclear_war_env.live_session import LiveSessionConfig
from nuclear_war_env.replay_validation import validate_replay_payload


def test_live_api_artifacts_returns_valid_replay_and_traces() -> None:
    server, thread, base_url = _start_server()
    try:
        artifacts = _json_request(base_url, "/artifacts")
    finally:
        _stop_server(server, thread)

    assert "replay" in artifacts
    assert artifacts["traces"] == []
    validate_replay_payload(artifacts["replay"], in_progress=True)


def test_live_api_step_agent_advances_agent_seat_decision() -> None:
    server, thread, base_url = _start_server(controlled_players=())
    try:
        decision = _json_request(base_url, "/decision")
        result = _json_request(
            base_url,
            "/step-agent",
            payload={"state_version": decision["state_version"]},
        )
    finally:
        _stop_server(server, thread)

    assert result["ok"] is True
    assert result["state_version"] == decision["state_version"] + 1
    assert result["decision"]["state_version"] == result["state_version"]


def test_live_api_decision_post_rejects_agent_seat_decision() -> None:
    server, thread, base_url = _start_server(controlled_players=())
    try:
        decision = _json_request(base_url, "/decision")
        action_id = decision["legal_actions"][0]["action_id"]
        with pytest.raises(HTTPError) as error:
            _json_request(
                base_url,
                "/decision",
                payload={
                    "state_version": decision["state_version"],
                    "action_id": action_id,
                },
            )
        payload = _error_payload(error.value)
        next_decision = _json_request(base_url, "/decision")
    finally:
        _stop_server(server, thread)

    assert error.value.code == 400
    assert payload["error"]["code"] == "agent_player"
    assert next_decision["state_version"] == decision["state_version"]


def _start_server(
    *, controlled_players: tuple[str, ...] = ("player_0",)
) -> tuple[ThreadingHTTPServer, Thread, str]:
    config = LiveSessionConfig(
        players=3,
        seed=42,
        max_turns=50,
        controlled_players=controlled_players,
    )
    server = create_live_api_server("127.0.0.1", 0, config)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _stop_server(server: ThreadingHTTPServer, thread: Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def _json_request(
    base_url: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base_url}{path}",
        data=data,
        method="POST" if payload is not None else "GET",
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=5) as response:
        assert response.headers["Content-Type"] == "application/json"
        return json.loads(response.read().decode("utf-8"))


def _error_payload(error: HTTPError) -> dict[str, Any]:
    assert error.headers["Content-Type"] == "application/json"
    return json.loads(error.read().decode("utf-8"))
