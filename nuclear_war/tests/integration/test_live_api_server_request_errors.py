from __future__ import annotations

import http.client
import json
import socket
from http.server import ThreadingHTTPServer
from threading import Thread

import pytest

from nuclear_war_env.live_api_protocol import MAX_BODY_BYTES
from nuclear_war_env.live_api_server import create_live_api_server
from nuclear_war_env.live_session import LiveSessionConfig


@pytest.mark.parametrize(
    ("headers", "body"),
    [
        ({"Content-Length": "abc"}, b"{}"),
        ({"Content-Length": "-1"}, b""),
        ({"Content-Length": str(MAX_BODY_BYTES + 1)}, b""),
        ({"Content-Length": "0"}, b""),
    ],
)
def test_live_api_rejects_invalid_content_length(
    headers: dict[str, str], body: bytes
) -> None:
    server, thread, port = _start_server()
    try:
        status, response_headers, payload = _request(
            port, "POST", "/step-agent", headers=headers, body=body
        )
    finally:
        _stop_server(server, thread)

    assert status == 400
    assert response_headers["Content-Type"] == "application/json"
    assert payload["ok"] is False
    assert payload["error"]["code"] == "invalid_body"


def test_live_api_rejects_missing_content_length() -> None:
    server, thread, port = _start_server()
    try:
        status, headers, payload = _raw_post_without_length(port)
    finally:
        _stop_server(server, thread)

    assert status == 400
    assert headers["Content-Type"] == "application/json"
    assert payload["error"]["code"] == "invalid_body"


@pytest.mark.parametrize("method", ["PUT", "TRACE", "CONNECT"])
def test_live_api_unsupported_method_returns_json_error(method: str) -> None:
    server, thread, port = _start_server()
    try:
        status, headers, payload = _request(
            port,
            method,
            "/decision",
            headers={"Origin": "http://localhost:5173"},
            body=b"",
        )
    finally:
        _stop_server(server, thread)

    assert status == 405
    assert headers["Content-Type"] == "application/json"
    assert headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert headers["Access-Control-Allow-Methods"] == "GET, POST, OPTIONS"
    assert payload["error"]["code"] == "method_not_allowed"


def _start_server() -> tuple[ThreadingHTTPServer, Thread, int]:
    config = LiveSessionConfig(players=3, seed=42, max_turns=50)
    server = create_live_api_server("127.0.0.1", 0, config)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_port


def _stop_server(server: ThreadingHTTPServer, thread: Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    assert not thread.is_alive()


def _request(
    port: int,
    method: str,
    path: str,
    *,
    headers: dict[str, str],
    body: bytes,
) -> tuple[int, http.client.HTTPMessage, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, response.headers, payload
    finally:
        conn.close()


def _raw_post_without_length(port: int) -> tuple[int, dict[str, str], dict]:
    request = (
        b"POST /step-agent HTTP/1.1\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Content-Type: application/json\r\n"
        b"Connection: close\r\n\r\n{}"
    )
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(request)
        raw = b""
        while chunk := sock.recv(4096):
            raw += chunk
    return _parse_raw_response(raw)


def _parse_raw_response(raw: bytes) -> tuple[int, dict[str, str], dict]:
    head, body = raw.split(b"\r\n\r\n", 1)
    lines = head.decode("iso-8859-1").split("\r\n")
    status = int(lines[0].split()[1])
    headers = dict(line.split(": ", 1) for line in lines[1:])
    return status, headers, json.loads(body.decode("utf-8"))
