import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any

from .live_api_protocol import (
    API_PATHS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    INVALID_JSON_BODY,
    UNKNOWN,
    VITE_ORIGINS,
    ApiRequestError,
    matches_type,
    parse_body_length,
)
from .live_session import LiveSession, LiveSessionConfig, LiveSessionError


def create_live_api_server(
    host: str, port: int, config: LiveSessionConfig
) -> ThreadingHTTPServer:
    session = LiveSession.start(config)
    lock = Lock()

    class LiveApiHandler(BaseHTTPRequestHandler):
        def do_OPTIONS(self) -> None:
            if self.path not in API_PATHS:
                self._send_api_error(ApiRequestError(404, "not_found", UNKNOWN))
                return
            self._send_json(200, {"ok": True})

        def do_PUT(self) -> None:
            error = ApiRequestError(405, "method_not_allowed", "Unsupported method.")
            self._send_api_error(error)

        do_PATCH = do_DELETE = do_HEAD = do_PUT

        def send_error(
            self,
            code: int,
            message: str | None = None,
            explain: str | None = None,
        ) -> None:
            if code == 501:
                self.do_PUT()
                return
            error = ApiRequestError(code, "http_error", message or "HTTP error.")
            self._send_api_error(error)

        def do_GET(self) -> None:
            routes = {
                "/session": session.session_payload,
                "/state": session.state_payload,
                "/decision": session.decision_payload,
                "/artifacts": session.artifacts_payload,
            }
            route = routes.get(self.path)
            if route is None:
                self._send_api_error(ApiRequestError(404, "not_found", UNKNOWN))
                return
            with lock:
                self._send_json(200, route())

        def do_POST(self) -> None:
            try:
                if self.path not in {"/decision", "/step-agent"}:
                    raise ApiRequestError(404, "not_found", UNKNOWN)
                schema: dict[str, type] = {"state_version": int}
                if self.path == "/decision":
                    schema["action_id"] = str
                payload = self._require_body(schema)
                with lock:
                    if self.path == "/decision":
                        result = session.apply_action_id(
                            payload["action_id"], payload["state_version"]
                        )
                    else:
                        result = session.step_agent(payload["state_version"])
            except ApiRequestError as exc:
                self._send_api_error(exc)
                return
            except LiveSessionError as exc:
                status = 409 if exc.code == "stale_state" else 400
                self._send_api_error(ApiRequestError(status, exc.code, str(exc)))
                return
            self._send_json(200, result)

        def log_message(self, _format: str, *_args: Any) -> None:
            return

        def _require_body(self, schema: dict[str, type]) -> dict[str, Any]:
            length = parse_body_length(self.headers.get("Content-Length"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ApiRequestError(400, "invalid_json", INVALID_JSON_BODY) from exc
            if not isinstance(payload, dict) or set(payload) != set(schema):
                raise ApiRequestError(400, "invalid_body", "Invalid request body.")
            for key, expected in schema.items():
                if not matches_type(payload[key], expected):
                    raise ApiRequestError(400, "invalid_body", "Invalid request body.")
            return payload

        def _send_api_error(self, error: ApiRequestError) -> None:
            self._send_json(
                error.status,
                {"ok": False, "error": {"code": error.code, "message": str(error)}},
            )

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(body)

        def _send_cors_headers(self) -> None:
            headers = getattr(self, "headers", None)
            origin = None if headers is None else headers.get("Origin")
            if origin in VITE_ORIGINS:
                self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    return ThreadingHTTPServer((host, port), LiveApiHandler)


def run_live_api_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    players: int = 3,
    seed: int = 42,
    max_turns: int = 50,
    controlled_players: tuple[str, ...] = ("player_0",),
) -> None:
    config = LiveSessionConfig(players, seed, max_turns, controlled_players)
    server = create_live_api_server(host, port, config)
    print(f"Serving live API at http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()
