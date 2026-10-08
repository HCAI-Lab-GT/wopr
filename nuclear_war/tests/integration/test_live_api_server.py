from __future__ import annotations

import json
from http.server import ThreadingHTTPServer
from threading import Thread
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from nuclear_war_env import cli
from nuclear_war_env.live_api_server import create_live_api_server
from nuclear_war_env.live_session import LiveSessionConfig


def test_live_api_get_endpoints_return_session_state_and_decision() -> None:
    server, thread, base_url = _start_server()
    try:
        session = _json_request(base_url, "/session")
        state = _json_request(base_url, "/state")
        decision = _json_request(base_url, "/decision")
    finally:
        _stop_server(server, thread)

    assert session["seed"] == 42
    assert session["players"] == ["player_0", "player_1", "player_2"]
    assert session["state_version"] == 1
    assert session["controlled_players"] == ["player_0"]
    assert state["players"][0]["player_id"] == "player_0"
    assert decision["pending"] is True
    assert decision["legal_actions"]


def test_live_api_decision_post_advances_state_version() -> None:
    server, thread, base_url = _start_server()
    try:
        decision = _json_request(base_url, "/decision")
        action_id = decision["legal_actions"][0]["action_id"]
        result = _json_request(
            base_url, "/decision", payload=_body(decision, action_id)
        )
    finally:
        _stop_server(server, thread)

    assert result["ok"] is True
    assert result["state_version"] == decision["state_version"] + 1
    assert result["decision"]["state_version"] == result["state_version"]


def test_live_api_decision_post_rejects_stale_state() -> None:
    server, thread, base_url = _start_server()
    try:
        decision = _json_request(base_url, "/decision")
        action_id = decision["legal_actions"][0]["action_id"]
        _json_request(base_url, "/decision", payload=_body(decision, action_id))
        with pytest.raises(HTTPError) as error:
            _json_request(base_url, "/decision", payload=_body(decision, action_id))
        payload = _error_payload(error.value)
    finally:
        _stop_server(server, thread)

    assert error.value.code == 409
    assert payload["error"]["code"] == "stale_state"


def test_live_api_options_returns_vite_cors_headers() -> None:
    server, thread, base_url = _start_server()
    try:
        request = Request(f"{base_url}/decision", method="OPTIONS")
        request.add_header("Origin", "http://localhost:5173")
        request.add_header("Access-Control-Request-Method", "POST")
        with urlopen(request, timeout=5) as response:
            headers = response.headers
            payload = json.loads(response.read().decode("utf-8"))
        with pytest.raises(HTTPError) as error:
            urlopen(Request(f"{base_url}/missing", method="OPTIONS"), timeout=5)
        missing = _error_payload(error.value)
    finally:
        _stop_server(server, thread)

    assert payload == {"ok": True}
    assert headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert headers["Access-Control-Allow-Methods"] == "GET, POST, OPTIONS"
    assert headers["Content-Type"] == "application/json"
    assert error.value.code == 404
    assert missing["error"]["code"] == "not_found"


def test_live_server_cli_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run_live_api_server(**kwargs: Any) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(cli, "run_live_api_server", fake_run_live_api_server)

    assert cli.main(["live-server"]) == 0
    assert captured == {
        "host": "127.0.0.1",
        "port": 8765,
        "players": 3,
        "seed": 42,
        "max_turns": 50,
        "controlled_players": ("player_0",),
    }


def test_live_server_cli_controlled_override_replaces_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run_live_api_server(**kwargs: Any) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(cli, "run_live_api_server", fake_run_live_api_server)

    assert cli.main(["live-server", "--controlled", "player_1"]) == 0
    assert captured["controlled_players"] == ("player_1",)


def _start_server() -> tuple[ThreadingHTTPServer, Thread, str]:
    config = LiveSessionConfig(players=3, seed=42, max_turns=50)
    server = create_live_api_server("127.0.0.1", 0, config)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _stop_server(server: ThreadingHTTPServer, thread: Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def _body(decision: dict[str, Any], action_id: str) -> dict[str, Any]:
    return {"state_version": decision["state_version"], "action_id": action_id}


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
